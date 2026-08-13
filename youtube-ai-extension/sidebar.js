// sidebar.js - Handles Extension Auth State & API Interactions

let currentAuthMode = "login"; // "login" or "register"

document.addEventListener("DOMContentLoaded", async () => {
    // 1. Initialize Auth module and check existing session
    await Auth.init();
    await updateUIBasedOnAuth();

    // 2. Setup Auth Event Listeners
    setupAuthListeners();

    // 3. Setup Chat & UI Listeners
    setupChatListeners();
});

// Update view state depending on login state
async function updateUIBasedOnAuth() {
    const token = await Auth.getToken();
    const user = await Auth.getUser();

    const authContainer = document.getElementById("authContainer");
    const mainAppContainer = document.getElementById("mainAppContainer");
    const userHeader = document.getElementById("userHeader");
    const userEmailEl = document.getElementById("userEmail");

    if (token) {
        // User is Logged In
        authContainer.classList.add("hidden");
        mainAppContainer.classList.remove("hidden");
        userHeader.classList.remove("hidden");

        if (user && user.email) {
            userEmailEl.innerText = user.email;
        } else {
            userEmailEl.innerText = "Authenticated User";
        }
    } else {
        // User is Logged Out
        authContainer.classList.remove("hidden");
        mainAppContainer.classList.add("hidden");
        userHeader.classList.add("hidden");
    }
}

// Setup Event Listeners for Auth (Login / Register / Logout)
function setupAuthListeners() {
    const tabLogin = document.getElementById("tabLogin");
    const tabRegister = document.getElementById("tabRegister");
    const authForm = document.getElementById("authForm");
    const logoutBtn = document.getElementById("logoutBtn");

    tabLogin.addEventListener("click", () => switchAuthMode("login"));
    tabRegister.addEventListener("click", () => switchAuthMode("register"));

    authForm.addEventListener("submit", handleAuthSubmit);
    logoutBtn.addEventListener("click", handleLogout);
}

// Toggle between Login and Register tabs
function switchAuthMode(mode) {
    currentAuthMode = mode;
    clearAlert();

    const tabLogin = document.getElementById("tabLogin");
    const tabRegister = document.getElementById("tabRegister");
    const authTitle = document.getElementById("authTitle");
    const authSubtitle = document.getElementById("authSubtitle");
    const authSubmitBtn = document.getElementById("authSubmitBtn");

    if (mode === "login") {
        tabLogin.classList.add("active");
        tabRegister.classList.remove("active");
        authTitle.innerText = "Welcome Back";
        authSubtitle.innerText = "Sign in with Supabase to analyze videos";
        authSubmitBtn.innerText = "Sign In";
    } else {
        tabRegister.classList.add("active");
        tabLogin.classList.remove("active");
        authTitle.innerText = "Create Account";
        authSubtitle.innerText = "Register with Supabase to get started";
        authSubmitBtn.innerText = "Register";
    }
}

// Handle Form Submission for Login / Registration
async function handleAuthSubmit(e) {
    e.preventDefault();
    clearAlert();

    const email = document.getElementById("authEmail").value.trim();
    const password = document.getElementById("authPassword").value;
    const submitBtn = document.getElementById("authSubmitBtn");

    if (!email || !password) {
        showAlert("Please fill in all fields", "error");
        return;
    }

    // Check if configuration has been updated
    if (CONFIG.SUPABASE_URL.includes("your-supabase-project")) {
        showAlert("Please update SUPABASE_URL and SUPABASE_ANON_KEY in config.js", "error");
        return;
    }

    submitBtn.disabled = true;
    submitBtn.innerText = currentAuthMode === "login" ? "Signing in..." : "Registering...";

    let result;
    if (currentAuthMode === "login") {
        result = await Auth.signIn(email, password);
    } else {
        result = await Auth.signUp(email, password);
    }

    submitBtn.disabled = false;
    submitBtn.innerText = currentAuthMode === "login" ? "Sign In" : "Register";

    if (result.success) {
        if (currentAuthMode === "register" && !result.data.access_token) {
            showAlert("Registration successful! Check your email to confirm registration.", "success");
        } else {
            showAlert("Successfully authenticated!", "success");
            setTimeout(async () => {
                await updateUIBasedOnAuth();
            }, 500);
        }
    } else {
        showAlert(result.error || "Authentication failed", "error");
    }
}

// Handle Logout
async function handleLogout() {
    await Auth.logout();
    await updateUIBasedOnAuth();
}

// Alert helper
function showAlert(message, type) {
    const alertEl = document.getElementById("authAlert");
    alertEl.innerText = message;
    alertEl.className = `alert ${type}`;
}

function clearAlert() {
    const alertEl = document.getElementById("authAlert");
    alertEl.innerText = "";
    alertEl.className = "alert hidden";
}

// Setup Event Listeners for Chat & Extension Sidebar
function setupChatListeners() {
    const askBtn = document.getElementById("askBtn");
    const closeBtn = document.getElementById("closeSidebar");

    if (askBtn) {
        askBtn.addEventListener("click", sendChatMessage);
    }

    if (closeBtn) {
        closeBtn.addEventListener("click", () => {
            window.parent.postMessage({ type: "CLOSE_AI_SIDEBAR" }, "*");
        });
    }
}

// Send chat message with Supabase Auth Token attached in Authorization Header
async function sendChatMessage() {
    const questionInput = document.getElementById("question");
    const query = questionInput.value.trim();
    if (!query) return;

    const token = await Auth.getToken();
    const user = await Auth.getUser();

    if (!token) {
        alert("Session expired. Please log in again.");
        await updateUIBasedOnAuth();
        return;
    }

    const typingIndicator = document.getElementById("typingIndicator");
    const responseContainer = document.getElementById("response");

    // Display indicator
    typingIndicator.classList.remove("hidden");
    responseContainer.classList.add("hidden");

    try {
        const [tab] = await chrome.tabs.query({
            active: true,
            currentWindow: true
        });

        const backendUrl = CONFIG.BACKEND_API_URL || "http://localhost:8000";

        // Fetch request with stored Bearer token header
        const response = await fetch(`${backendUrl}/chat`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${token}`
            },
            body: JSON.stringify({
                query: query,
                user_id: user ? user.id : "1"
            })
        });

        const data = await response.json();

        typingIndicator.classList.add("hidden");
        responseContainer.classList.remove("hidden");

        if (response.ok) {
            responseContainer.innerText = data.response || data.response[0].text || "No response received.";
        } else {
            responseContainer.innerText = `Error: ${data.detail || "Failed to process query."}`;
        }
    } catch (error) {
        console.error("Fetch Error:", error);
        typingIndicator.classList.add("hidden");
        responseContainer.classList.remove("hidden");
        responseContainer.innerText = "Error connecting to backend server. Make sure FastAPI server is running.";
    }
}
