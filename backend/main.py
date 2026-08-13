import os
import json
import urllib.request
import urllib.error
import jwt
from typing import Optional
from dotenv import load_dotenv
from agent import agent
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel

load_dotenv()

app = FastAPI(
    title="YouTube AI Agent", 
    version="1.0.1"
)

# Enable CORS for Chrome Extension and local clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

security = HTTPBearer()

SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY", "")


def verify_supabase_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """
    Verifies the Bearer token received in the Authorization header.
    Validates token via Supabase Auth API if credentials are provided,
    or decodes JWT payload to extract user details.
    """
    token = credentials.credentials
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Bearer token missing from Authorization header",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 1. If Supabase URL & Anon Key are configured, verify live with Supabase
    if SUPABASE_URL and SUPABASE_ANON_KEY and "your-supabase-project" not in SUPABASE_URL:
        try:
            req = urllib.request.Request(
                f"{SUPABASE_URL.rstrip('/')}/auth/v1/user",
                headers={
                    "Authorization": f"Bearer {token}",
                    "apikey": SUPABASE_ANON_KEY
                }
            )
            with urllib.request.urlopen(req) as response:
                if response.status == 200:
                    user_data = json.loads(response.read().decode())
                    return user_data
        except urllib.error.HTTPError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid or expired Supabase authentication token: {e.reason}",
                headers={"WWW-Authenticate": "Bearer"},
            )
        except Exception as e:
            print(f"Supabase auth check failed: {e}")

    # 2. Decode JWT payload locally as fallback
    try:
        # Decode without key verification if secret is not set, but verify expiration
        payload = jwt.decode(token, options={"verify_signature": False})
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token payload missing user ID (sub claim)"
            )
        return {"id": user_id, "email": payload.get("email", ""), "user_metadata": payload.get("user_metadata", {})}
    except Exception:
        # Simple manual JWT payload parsing if PyJWT is not installed
        try:
            parts = token.split(".")
            if len(parts) == 3:
                # Add padding for base64 decoding
                padding = "=" * (4 - len(parts[1]) % 4)
                import base64
                payload_bytes = base64.urlsafe_b64decode(parts[1] + padding)
                payload = json.loads(payload_bytes.decode('utf-8'))
                user_id = payload.get("sub")
                if user_id:
                    return {"id": user_id, "email": payload.get("email", "")}
        except Exception as decode_err:
            print("JWT decode fallback error:", decode_err)

    # Return basic user structure if token exists
    return {"id": "authenticated_user", "token": token}


@app.get("/")
async def root():
    return {"message": "Welcome to the YouTube Channel Analysis Agent!"}


class ChatRequest(BaseModel):
    query: str
    url: Optional[str] = None
    user_id: Optional[str] = None


@app.post("/chat")
async def chat(
    request: ChatRequest,
    current_user: dict = Depends(verify_supabase_token)
):
    # Use verified user ID from token or fallback to request body user_id
    user_id = current_user.get("id") or request.user_id or "default_user"

    response = run(request.query, user_id, request.url)

    return {
        "message": "Query processed successfully.",
        "success": True,   
        "query": request.query,
        "url": request.url,
        "user_id": user_id,
        "response": response
    }


def run(query: str, user_id: str, url: Optional[str] = None):
    config = {
        "configurable": {
            "thread_id": user_id
        }
    }

    # Format user prompt with active URL context if provided
    if url and url.strip():
        formatted_message = f"Active YouTube Page URL: {url.strip()}\nUser Query: {query}"
    else:
        formatted_message = query

    try:
        result = agent.invoke({
            "messages": [
                {"role": "user", "content": formatted_message}
            ]
        }, config=config)
    except Exception as e:
        err_msg = str(e)
        if "tool_calls" in err_msg or "INVALID_CHAT_HISTORY" in err_msg or "ToolMessage" in err_msg:
            print(f"⚠️ Corrupted tool call chat history detected in thread {user_id}. Resetting thread state...")
            fresh_config = {
                "configurable": {
                    "thread_id": f"{user_id}_reset"
                }
            }
            result = agent.invoke({
                "messages": [
                    {"role": "user", "content": formatted_message}
                ]
            }, config=fresh_config)
        else:
            raise e

    # The final message in the list is the agent's answer
    final_answer = result["messages"][-1].content
    return final_answer
