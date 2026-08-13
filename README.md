# 🤖 YouTube AI Assistant - Chrome Extension & ReAct Agent Backend

A full-stack, AI-powered Chrome Extension and modular FastAPI backend that brings Google Gemini-style video analysis, channel intelligence, sentiment analytics, and playlist inspection directly to your YouTube browser experience.

Powered by **LangGraph**, **LangChain**, **FastAPI**, **Supabase Auth**, and local/cloud LLMs (such as Ollama `qwen3:4b`, Groq `llama-3.1-8b`, or Google `gemini-2.5-flash`).

---

## 🌟 Key Features

- ⚡ **Real-Time Token Streaming**: Streams LLM token responses word-by-word into the Chrome extension live via a dedicated `/chat/stream` SSE endpoint (`StreamingResponse` + LangGraph `astream_events`).
- 🎥 **Context-Aware YouTube Analysis**: Automatically detects active YouTube URLs (Video, Channel, Playlist, or Homepage) and extracts relevant IDs without manual input.
- 🔐 **Supabase Authentication**: Full Login & Register user management integrated directly into the Chrome extension with JWT token storage in `localStorage` and `chrome.storage.local`.
- 🧱 **Modular FastAPI Architecture**: Clean separation of concerns across authentication, API routes, request schemas, services, and ReAct tools.
- 🛡️ **Dual Endpoints & Secure Token Verification**: Supports both `/chat` (standard JSON) and `/chat/stream` (real-time stream), protected by FastAPI `HTTPBearer` security middleware.
- 🎨 **Modern Glassmorphic Sidebar UI**: Sleek dark-mode extension sidebar with auto-scrolling conversation bubbles, animated typing indicators, and auto-hiding floating action button.
- 🧠 **22 Specialized AI Tools**: Comprehensive tool suite for channel growth, video specs, sentiment analysis, comment topic mining, playlist contents, and global trending search.
- 🤖 **LLM Provider Agnostic**: Configured to run seamlessly on lightweight local models (`qwen3:4b` via Ollama) as well as cloud LLMs (Groq, Gemini).

---

## 📁 Modular Project Architecture

```text
youtube-ai-agent/
│
├── youtube-ai-extension/          # Chrome Extension Manifest V3 Frontend
│   ├── manifest.json              # Extension manifest & permissions
│   ├── content.js                 # Content script for modern floating action button (FAB)
│   ├── sidebar.html               # Main extension sidebar UI structure
│   ├── sidebar.css                # Glassmorphism dark-theme styling
│   ├── sidebar.js                 # Chat UI logic, real-time ReadableStream reader & URL context
│   ├── auth.js                    # Supabase Auth REST API client & storage manager
│   └── config.js                  # Supabase credentials & streaming endpoint configuration
│
└── backend/                       # FastAPI & LangGraph AI Agent Backend
    ├── main.py                    # Entry point initializing FastAPI app & mounting routers
    ├── agent.py                   # LangGraph ReAct agent & prompt engineering
    ├── .env                       # Environment variables (YouTube API key, Supabase credentials)
    ├── requirements.txt           # Python dependencies
    │
    ├── auth/                      # Authentication Layer
    │   └── auth.py                # Supabase JWT token verification & HTTPBearer security
    │
    ├── routes/                    # API Route Controllers
    │   └── chat_routes.py         # /chat (JSON) & /chat/stream (SSE) endpoints with memory recovery
    │
    ├── schemas/                   # Pydantic Request & Response Data Schemas
    │   └── chat_schema.py         # ChatRequest model (query, url, user_id)
    │
    ├── services/                  # Business Logic & Service Layers
    │
    └── tools/                     # 22 Specialized YouTube Intelligence Tools
        ├── channel_tools.py       # Channel stats, handles, comparisons, growth & age
        ├── video_tools.py         # Video stats, specs, duration, tags & comments
        ├── playlist_tools.py      # Playlists & playlist video items inspection
        ├── research_tools.py      # Trending, global search, upload frequency & engagement rate
        ├── sentiment_tools.py     # VADER sentiment analysis & comment topic extraction
        └── transcript_tools.py    # YouTube video captions & transcript extraction
```

---

## 🔌 API Endpoints Summary

| Method | Endpoint | Response Type | Description |
| :--- | :--- | :--- | :--- |
| `POST` | `/chat` | `application/json` | Standard endpoint returning the complete answer in a single JSON payload |
| `POST` | `/chat/stream` | `text/event-stream` | **Real-time streaming endpoint** emitting LLM token chunks live as they are generated |
| `GET` | `/` | `application/json` | Server health check endpoint |

---

## 🛠️ Complete Suite of 22 Agent Tools

| Category | Tool Name | Description |
| :--- | :--- | :--- |
| **Channel Analytics** | `get_channel_info_by_id` | Gets channel subscriber, view, and video count by ID |
| | `search_channel_by_name` | Searches channels by creator or brand name |
| | `get_channel_by_handle` | Fetches channel metadata by `@handle` |
| | `compare_channels` | Compares multiple channels side-by-side |
| | `extract_channel_topics` | Mines top content topics from video titles |
| | `estimate_channel_growth_and_age` | Computes channel age, avg views/video & sub efficiency |
| | `get_channel_sections` | Inspects channel home tab layout sections |
| **Video Intelligence** | `get_recent_videos` | Fetches recent uploads from a channel |
| | `get_video_stats` | Fetches view count, like count, and comment count |
| | `get_video_details` | Returns human duration (e.g. `14m 20s`), SEO tags, HD/SD spec |
| | `get_video_comments` | Retrieves top comments with author & like count |
| | `search_channel_videos` | Keyword video search within a channel |
| **Transcripts** | `get_video_transcript` | Extracts full text video captions/transcripts |
| **Sentiment & Topics** | `get_comment_sentiment` | VADER sentiment breakdown (% positive, negative, neutral) |
| | `extract_comment_topics` | Mines top 15 discussion keywords from video comments |
| **Playlists** | `get_channel_playlists` | Lists public playlists of a channel |
| | `get_playlist_videos` | Lists videos inside a specific playlist with titles and order |
| **Research & Global** | `get_trending_videos` | Fetches top trending videos by region |
| | `search_global_videos` | Searches across YouTube globally for any query |
| | `analyze_upload_frequency` | Computes average uploads per week |
| | `get_top_performing_videos` | Returns top 10 most viewed channel videos |
| | `calculate_channel_engagement_rate` | Calculates engagement rate `%` (`((Likes + Comments) / Views) * 100`) |

---

## ⚡ Quick Start & Setup

### 1. Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv myvenv
   # On Windows:
   myvenv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file in the `backend/` directory:
   ```env
   YOUTUBE_API_KEY=your_youtube_data_api_key
   SUPABASE_URL=https://your-project.supabase.co
   SUPABASE_ANON_KEY=your-supabase-anon-key
   GEMINI_API_KEY=your_gemini_api_key
   GROQ_API_KEY=your_groq_api_key
   ```

5. Start the FastAPI server:
   ```bash
   uvicorn main:app --reload --port 8000
   ```
   *The server will run on `http://localhost:8000`.*

---

### 2. Chrome Extension Setup

1. Open `youtube-ai-extension/config.js` and configure endpoints and streaming toggle:
   ```javascript
   const CONFIG = {
       SUPABASE_URL: "https://your-project.supabase.co",
       SUPABASE_ANON_KEY: "your-supabase-anon-key",
       BACKEND_API_URL: "http://localhost:8000",

       // Set to true to stream tokens live (/chat/stream) or false for standard JSON (/chat)
       ENABLE_STREAMING: true,
       CHAT_ENDPOINT: "/chat",
       STREAM_ENDPOINT: "/chat/stream"
   };
   ```

2. Open Google Chrome and navigate to `chrome://extensions`.
3. Enable **Developer mode** (top right toggle).
4. Click **Load unpacked** and select the `youtube-ai-extension` folder.
5. Open any YouTube page (e.g. `youtube.com/watch?v=...`) and click the modern **YouTube AI** floating button to start!

---

## 🧪 Testing Guide

| Page Type | Example Query to Ask | Tools Tested |
| :--- | :--- | :--- |
| **Video Page** | *"Summarize this video and analyze comment sentiment."* | `get_video_transcript`, `get_comment_sentiment` |
| **Channel Page** | *"What is the engagement rate and upload frequency of this channel?"* | `calculate_channel_engagement_rate`, `analyze_upload_frequency` |
| **Playlist Page** | *"List the videos inside this playlist with their titles."* | `get_playlist_videos` |
| **Home Page** | *"What are the top trending videos right now in the US?"* | `get_trending_videos`, `search_global_videos` |

