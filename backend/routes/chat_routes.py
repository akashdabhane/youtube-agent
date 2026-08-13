from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from schemas.chat_schema import ChatRequest
from typing import Optional
from agent import agent
from auth.auth import verify_supabase_token
import asyncio

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


async def generate_stream_response(query: str, user_id: str, url: Optional[str] = None):
    """
    Asynchronously stream LLM token responses event-by-event using LangGraph's astream_events.
    """
    config = {
        "configurable": {
            "thread_id": user_id
        }
    }

    if url and url.strip():
        formatted_message = f"Active YouTube Page URL: {url.strip()}\nUser Query: {query}"
    else:
        formatted_message = query

    input_payload = {
        "messages": [
            {"role": "user", "content": formatted_message}
        ]
    }

    try:
        async for event in agent.astream_events(input_payload, config=config, version="v2"):
            kind = event.get("event")
            if kind == "on_chat_model_stream":
                chunk = event["data"]["chunk"]
                if hasattr(chunk, "content") and chunk.content:
                    yield chunk.content
    except Exception as e:
        err_msg = str(e)
        if "tool_calls" in err_msg or "INVALID_CHAT_HISTORY" in err_msg or "ToolMessage" in err_msg:
            print(f"⚠️ Corrupted tool call chat history in stream thread {user_id}. Resetting thread state...")
            fresh_config = {
                "configurable": {
                    "thread_id": f"{user_id}_reset"
                }
            }
            async for event in agent.astream_events(input_payload, config=fresh_config, version="v2"):
                if event.get("event") == "on_chat_model_stream":
                    chunk = event["data"]["chunk"]
                    if hasattr(chunk, "content") and chunk.content:
                        yield chunk.content
        else:
            print(f"Streaming Error: {e}")
            yield f"\n[Error during streaming: {str(e)}]"


@router.post("/stream")
async def chat_stream(
    request: ChatRequest,
    current_user: dict = Depends(verify_supabase_token)
):
    """
    Real-time streaming endpoint returning token chunks as text/event-stream.
    """
    user_id = current_user.get("id") or request.user_id or "default_user"
    return StreamingResponse(
        generate_stream_response(request.query, user_id, request.url),
        media_type="text/event-stream"
    )
