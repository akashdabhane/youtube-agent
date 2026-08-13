// Configuration for Supabase and Backend API
const CONFIG = {
    // Replace with your Supabase Project URL and Anon Key
    SUPABASE_URL: "https://vkyyuapmzxbbcyziawgh.supabase.co",
    SUPABASE_ANON_KEY: "sb_publishable_amL8zKgzPyNtlQtNtVlJpg_XAp7X4bb",
    
    // FastAPI Backend URL
    BACKEND_API_URL: "http://localhost:8000"
};

// Export to window object for browser extension scripts
window.CONFIG = CONFIG;
