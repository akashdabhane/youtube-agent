// Configuration for Supabase and Backend API
const CONFIG = {
    // Replace with your Supabase Project URL and Anon Key
    SUPABASE_URL: "https://vkyyuapmzxbbcyziawgh.supabase.co",
    SUPABASE_ANON_KEY: "sb_publishable_amL8zKgzPyNtlQtNtVlJpg_XAp7X4bb",
    
    // FastAPI Backend URL
    BACKEND_API_URL: "http://localhost:8000",

    // Set to true to use real-time streaming (/chat/stream), or false for standard response (/chat)
    ENABLE_STREAMING: true,
    CHAT_ENDPOINT: "/chat",
    STREAM_ENDPOINT: "/chat/stream"
};

// Export to window object for browser extension scripts
window.CONFIG = CONFIG;
