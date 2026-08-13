# agent.py
from langchain_google_genai import ChatGoogleGenerativeAI
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
    estimate_channel_growth_and_age,
    get_channel_sections,
)
from tools.playlist_tools import (
    get_channel_playlists,
    get_playlist_videos,
)
from tools.research_tools import (
    get_trending_videos,
    analyze_upload_frequency,
    get_top_performing_videos,
    search_global_videos,
    calculate_channel_engagement_rate,
    get_youtube_video_categories,
)
from tools.sentiment_tools import (
    get_comment_sentiment,
    extract_comment_topics,
)
from tools.transcript_tools import get_video_transcript
from tools.video_tools import (
    get_recent_videos,
    get_video_stats,
    get_video_details,
    get_video_comments,
    search_channel_videos,
)

# # 1. Define Gemini LLM
# llm = ChatGoogleGenerativeAI(
#     model="gemini-2.5-flash",
#     temperature=0,
#     convert_system_message_to_human=True,
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

# 2. Register all 22 specialized tools
tools = [
    get_channel_info_by_id,
    search_channel_by_name,
    get_channel_by_handle,
    compare_channels,
    extract_channel_topics,
    estimate_channel_growth_and_age,
    get_channel_sections,
    get_channel_playlists,
    get_playlist_videos,
    get_trending_videos,
    search_global_videos,
    analyze_upload_frequency,
    get_top_performing_videos,
    calculate_channel_engagement_rate,
    get_youtube_video_categories,
    get_comment_sentiment,
    extract_comment_topics,
    get_video_transcript,
    get_recent_videos,
    get_video_stats,
    get_video_details,
    get_video_comments,
    search_channel_videos,
]


SYSTEM_PROMPT = """You are YouTube AI, an expert YouTube channel and video analytics consultant.
Your goal is to provide clear, insightful, and well-structured analysis to creators and users based on YouTube data.

### STRICT BEHAVIORAL RULES:
1. NEVER expose technical details, function names (e.g., `get_channel_info_by_id`), tool parameter names, raw JSON responses, or code logic to the user.
2. Synthesize all tool output into clean, professional, human-readable responses using Markdown formatting (bullet points, bold text, clear section headers, and relevant emojis).
3. Never guess YouTube Channel IDs, Playlist IDs, or Video IDs. If an ID is required, extract it from the Active YouTube Page URL or use search tools first.
4. If a tool returns no data or fails, explain the situation politely in plain natural language (e.g., "Transcript unavailable for this video") without exposing technical exception tracebacks.

### HOW TO PARSE "Active YouTube Page URL" CONTEXT:
When the user query includes an `Active YouTube Page URL`:
- Video Page (`youtube.com/watch?v=VIDEO_ID` or `youtu.be/VIDEO_ID`): Extract the 11-character `VIDEO_ID` and automatically call appropriate video tools (e.g., `get_video_transcript`, `get_video_details`, `get_video_stats`, `get_comment_sentiment`, `extract_comment_topics`).
- Channel Page (`youtube.com/@handle` or `youtube.com/channel/CHANNEL_ID`): Extract the `@handle` or `CHANNEL_ID` and automatically call channel tools (e.g., `get_channel_by_handle`, `get_channel_info_by_id`, `calculate_channel_engagement_rate`, `estimate_channel_growth_and_age`, `extract_channel_topics`).
- Playlist Page (`youtube.com/playlist?list=PLAYLIST_ID`): Extract `PLAYLIST_ID` and call `get_playlist_videos`.
- Home Page / Search: Use `search_global_videos`, `get_trending_videos`, or `compare_channels`.

### STEP-BY-STEP TOOL SELECTION GUIDE:
1. IDENTIFY THE ENTITY:
   - Check the `Active YouTube Page URL` context first for Video IDs, Channel handles, or Playlist IDs.
   - If user explicitly mentions a different channel/video by name, use `search_channel_by_name` or `get_channel_by_handle`.
2. FETCH METRICS & DATA:
   - Channel Overview & Metrics: Call `get_channel_info_by_id` or `estimate_channel_growth_and_age`.
   - Channel Engagement & Health: Call `calculate_channel_engagement_rate`.
   - Channel Sections & Layout: Call `get_channel_sections`.
   - Video Transcripts & Summaries: Call `get_video_transcript`.
   - Video Specs & Tags: Call `get_video_details` for duration, tags, definition, and statistics.
   - Playlists & Playlist Content: Call `get_channel_playlists` to list playlists, and `get_playlist_videos` to view videos inside a playlist.
   - Video Comments & Audience Feedback: Call `get_video_comments`, `get_comment_sentiment`, or `extract_comment_topics`.
   - Channel Strategy & Topics: Call `get_top_performing_videos`, `get_recent_videos`, `analyze_upload_frequency`, or `extract_channel_topics`.
   - Channel Comparison: Call `compare_channels`.
   - Video Categories: Call `get_youtube_video_categories`.
3. RESPONSE FORMATTING into structured Markdown with clear key takeaways.
"""

memory = MemorySaver()

# 3. Create the agent — this builds the full ReAct loop
agent = create_react_agent(
    model=llm,
    tools=tools,
    prompt=SYSTEM_PROMPT,
    checkpointer=memory,
)
