from fastapi import APIRouter, Depends
from schemas.chat_schema import ChatRequest
from typing import Optional
from agent import agent
from auth.auth import verify_supabase_token


router = APIRouter(
    prefix="/chat",
    tags=["Chat"],
)


@router.post("/")
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


