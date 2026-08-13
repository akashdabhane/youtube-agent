// sidebar.js - Handles Extension Auth State & Dynamic Chat Messages

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

        updateActionsVisibility();
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
    const questionInput = document.getElementById("question");
    const actionBtns = document.querySelectorAll(".action-btn");

    if (askBtn) {
        askBtn.addEventListener("click", sendChatMessage);
    }

    // Support Enter key press to send message (Shift+Enter for newline)
    if (questionInput) {
        questionInput.addEventListener("keydown", (e) => {
            if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                sendChatMessage();
            }
        });
    }

    // Quick Action Buttons click handler
    actionBtns.forEach((btn) => {
        btn.addEventListener("click", () => {
            const presetQuery = btn.dataset.query;
            if (presetQuery && questionInput) {
                questionInput.value = presetQuery;
                sendChatMessage();
            }
        });
    });

    if (closeBtn) {
        closeBtn.addEventListener("click", () => {
            window.parent.postMessage({ type: "CLOSE_AI_SIDEBAR" }, "*");
        });
    }
}

// Hide quick action buttons if any user message is present in the chat
function updateActionsVisibility() {
    const actionsContainer = document.getElementById("actionsContainer");
    const userMessages = document.querySelectorAll("#chatContainer .user-message");

    if (actionsContainer) {
        if (userMessages.length > 0) {
            actionsContainer.classList.add("hidden");
        } else {
            actionsContainer.classList.remove("hidden");
        }
    }
}

// Auto-scroll chat container to the bottom
function scrollToBottom() {
    const chatContainer = document.getElementById("chatContainer");
    if (chatContainer) {
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }
}

// Send chat message and dynamically render user & AI response bubbles sequentially
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

    const chatContainer = document.getElementById("chatContainer");
    const typingIndicator = document.getElementById("typingIndicator");

    // 1. Clear input box immediately
    questionInput.value = "";

    // 2. Append User Message Bubble directly to chatContainer (Right Side)
    const userMessageDiv = document.createElement("div");
    userMessageDiv.className = "user-message";
    userMessageDiv.innerText = query;
    chatContainer.appendChild(userMessageDiv);

    // Hide Quick Actions section as soon as user sends a message
    updateActionsVisibility();

    // 3. Move and Show Typing Indicator at the absolute bottom
    chatContainer.appendChild(typingIndicator);
    typingIndicator.classList.remove("hidden");
    scrollToBottom();

    try {
        const backendUrl = CONFIG.BACKEND_API_URL || "http://localhost:8000";

        // 4. Fetch request with Bearer token header
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

        // 5. Hide typing indicator
        typingIndicator.classList.add("hidden");

        // 6. Append AI Response Bubble directly to chatContainer (Left Side)
        const aiMessageDiv = document.createElement("div");
        aiMessageDiv.className = "ai-message";

        if (response.ok) {
            aiMessageDiv.innerText = data.response || "No response received.";
        } else {
            aiMessageDiv.innerText = `Error: ${data.detail || "Failed to process query."}`;
        }

        chatContainer.appendChild(aiMessageDiv);
        scrollToBottom();

    } catch (error) {
        console.error("Fetch Error:", error);

        // Hide typing indicator
        typingIndicator.classList.add("hidden");

        // Append Error Message Bubble
        const errorMessageDiv = document.createElement("div");
        errorMessageDiv.className = "ai-message";
        errorMessageDiv.innerText = "Error connecting to backend server. Make sure FastAPI server is running.";
        chatContainer.appendChild(errorMessageDiv);
        scrollToBottom();
    }
}
