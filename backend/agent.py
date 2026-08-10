# agent.py
from langchain_google_genai import ChatGoogleGenerativeAI  # ← only this changes
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver
from langchain_groq import ChatGroq
from langchain_ollama import ChatOllama


from tools.channel_tools import (
    get_channel_info_by_id,
    search_channel_by_name,
    get_channel_by_handle,
    compare_channels,
    extract_channel_topics,
)
from tools.playlist_tools import get_channel_playlists
from tools.research_tools import (
    get_trending_videos,
    analyze_upload_frequency,
    get_top_performing_videos,
)
from tools.sentiment_tools import get_comment_sentiment
from tools.transcript_tools import get_video_transcript
from tools.video_tools import (
    get_recent_videos,
    get_video_stats,
    get_video_comments,
    search_channel_videos,
)

# # 1. Define  Gemini LLM
# llm = ChatGoogleGenerativeAI(
#     model="gemini-2.5-flash",
#     temperature=0,
#     convert_system_message_to_human=True,  # ← required for Gemini
# )

# # 1. Define GROQ LLM
# llm = ChatGroq(
#     model="llama-3.1-8b-instant",
#     temperature=0,
# )

# 1. Define Ollama LLM
llm = ChatOllama(
    model="qwen3:4b",
    temperature=0,
)

# 2. Register all your tools in a list
tools = [
    get_channel_info_by_id,
    search_channel_by_name,
    get_channel_by_handle,
    compare_channels,
    extract_channel_topics,
    get_channel_playlists,
    get_trending_videos,
    analyze_upload_frequency,
    get_top_performing_videos,
    get_comment_sentiment,
    get_video_transcript,
    get_recent_videos,
    get_video_stats,
    get_video_comments,
    search_channel_videos,
]


memory = MemorySaver()

# 3. Create the agent — this builds the full ReAct loop for you
agent = create_react_agent(
    model=llm,
    tools=tools,
    prompt="""
    You are a YouTube channel research assistant.
    When given a query, you will use the tools provided to gather information about YouTube channels, videos, and related data.
    You will then analyze the information and provide a comprehensive answer to the user's query.

    Always use tools step by step. Never guess channel IDs.
    """,
    checkpointer=memory,
)
