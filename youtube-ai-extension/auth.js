// auth.js - Supabase Authentication & Token Management for Chrome Extension

const Auth = {
    // Sign up a new user via Supabase Auth REST API
    async signUp(email, password) {
        try {
            const response = await fetch(`${CONFIG.SUPABASE_URL}/auth/v1/signup`, {
                method: "POST",
                headers: {
                    "apikey": CONFIG.SUPABASE_ANON_KEY,
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({ email, password })
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.msg || data.error_description || data.message || "Failed to register");
            }

            // If user confirmation is disabled in Supabase, session with token is returned directly
            if (data.access_token) {
                await this.saveSession(data);
            }

            return { success: true, data };
        } catch (error) {
            console.error("SignUp Error:", error);
            return { success: false, error: error.message };
        }
    },


    // Sign in an existing user via Supabase Auth REST API
    async signIn(email, password) {
        try {
            const response = await fetch(`${CONFIG.SUPABASE_URL}/auth/v1/token?grant_type=password`, {
                method: "POST",
                headers: {
                    "apikey": CONFIG.SUPABASE_ANON_KEY,
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({ email, password })
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error_description || data.msg || data.message || "Invalid credentials");
            }

            await this.saveSession(data);
            return { success: true, data };
        } catch (error) {
            console.error("SignIn Error:", error);
            return { success: false, error: error.message };
        }
    },


    // Save session data (tokens & user details) to localStorage and chrome.storage.local
    async saveSession(sessionData) {
        const accessToken = sessionData.access_token;
        const refreshToken = sessionData.refresh_token;
        const user = sessionData.user;

        // 1. Save to LocalStorage
        if (accessToken) localStorage.setItem("supabase_access_token", accessToken);
        if (refreshToken) localStorage.setItem("supabase_refresh_token", refreshToken);
        if (user) localStorage.setItem("supabase_user", JSON.stringify(user));

        // 2. Save to Chrome Extension Local Storage
        if (typeof chrome !== "undefined" && chrome.storage && chrome.storage.local) {
            await chrome.storage.local.set({
                supabase_access_token: accessToken,
                supabase_refresh_token: refreshToken,
                supabase_user: user
            });
        }
    },


    // Retrieve the access token from localStorage or chrome.storage
    async getToken() {
        let token = localStorage.getItem("supabase_access_token");

        if (!token && typeof chrome !== "undefined" && chrome.storage && chrome.storage.local) {
            const result = await chrome.storage.local.get(["supabase_access_token"]);
            token = result.supabase_access_token || null;
            if (token) {
                localStorage.setItem("supabase_access_token", token);
            }
        }

        return token;
    },


    // Retrieve current stored user details
    async getUser() {
        let userStr = localStorage.getItem("supabase_user");
        let user = userStr ? JSON.parse(userStr) : null;

        if (!user && typeof chrome !== "undefined" && chrome.storage && chrome.storage.local) {
            const result = await chrome.storage.local.get(["supabase_user"]);
            user = result.supabase_user || null;
            if (user) {
                localStorage.setItem("supabase_user", JSON.stringify(user));
            }
        }

        return user;
    },


    // Clear session (Logout)
    async logout() {
        localStorage.removeItem("supabase_access_token");
        localStorage.removeItem("supabase_refresh_token");
        localStorage.removeItem("supabase_user");

        if (typeof chrome !== "undefined" && chrome.storage && chrome.storage.local) {
            await chrome.storage.local.remove([
                "supabase_access_token",
                "supabase_refresh_token",
                "supabase_user"
            ]);
        }
    },

    
    // Initialize/Sync storage on extension view load
    async init() {
        if (typeof chrome !== "undefined" && chrome.storage && chrome.storage.local) {
            const result = await chrome.storage.local.get(["supabase_access_token", "supabase_user"]);
            if (result.supabase_access_token) {
                localStorage.setItem("supabase_access_token", result.supabase_access_token);
            }
            if (result.supabase_user) {
                localStorage.setItem("supabase_user", JSON.stringify(result.supabase_user));
            }
        }
    }
};

window.Auth = Auth;
