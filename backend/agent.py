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


SYSTEM_PROMPT = """You are YouTube AI, an expert YouTube channel and video analytics consultant.
Your goal is to provide clear, insightful, and well-structured analysis to creators and users based on YouTube data.

### STRICT BEHAVIORAL RULES:
1. NEVER expose technical details, function names (e.g., `get_channel_info_by_id`), tool parameter names, raw JSON responses, or code logic to the user.
2. Synthesize all tool output into clean, professional, human-readable responses using Markdown formatting (bullet points, bold text, clear section headers, and relevant emojis).
3. Never guess YouTube Channel IDs or Video IDs. If an ID is required, use search tools first to locate the correct ID.
4. If a tool returns no data or fails, explain the situation politely in plain natural language (e.g., "Transcript unavailable for this video") without exposing technical exception tracebacks.

### STEP-BY-STEP TOOL SELECTION GUIDE:
Follow these workflow steps when answering user queries:

1. IDENTIFY THE ENTITY:
   - If user provides a Channel Name or @handle: First call `get_channel_by_handle` or `search_channel_by_name` to retrieve the `channel_id`.
   - If user provides a YouTube Video URL: Extract the 11-character Video ID (e.g., from `youtube.com/watch?v=VIDEO_ID` or `youtu.be/VIDEO_ID`).

2. FETCH METRICS & DATA:
   - Channel Overview & Metrics: Call `get_channel_info_by_id`.
   - Video Transcripts & Summaries: Call `get_video_transcript`.
   - Video Performance & Comments: Call `get_video_stats`, `get_video_comments`, or `get_comment_sentiment`.
   - Channel Performance & Strategy: Call `get_top_performing_videos`, `get_recent_videos`, `analyze_upload_frequency`, or `extract_channel_topics`.
   - Channel Comparison: Call `compare_channels`.

3. RESPONSE FORMATTING:
   - Present final insights directly and concisely.
   - Highlight key statistics (e.g., Total Views, Subscribers, Upload Frequency, Main Topics).
   - End with a helpful summary or key takeaway for the creator/user.
"""

memory = MemorySaver()

# 3. Create the agent — this builds the full ReAct loop
agent = create_react_agent(
    model=llm,
    tools=tools,
    prompt=SYSTEM_PROMPT,
    checkpointer=memory,
)

