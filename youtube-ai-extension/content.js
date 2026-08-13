if (!document.getElementById("youtube-ai-fab-container")) {

    // 1. Inject Style sheet for animations & modern glassmorphic FAB
    const style = document.createElement("style");
    style.id = "youtube-ai-fab-styles";
    style.textContent = `
        @keyframes yt-ai-pulse {
            0%, 100% {
                box-shadow: 0 8px 24px rgba(255, 0, 51, 0.45), 0 0 0 0 rgba(255, 0, 51, 0.35);
            }
            50% {
                box-shadow: 0 12px 32px rgba(255, 0, 51, 0.65), 0 0 0 12px rgba(255, 0, 51, 0);
            }
        }

        @keyframes yt-ai-shimmer {
            0% { background-position: -200% 0; }
            100% { background-position: 200% 0; }
        }

        .yt-ai-fab {
            position: fixed;
            right: 28px;
            bottom: 75px;
            height: 52px;
            padding: 0 20px;
            border-radius: 26px;
            background: linear-gradient(135deg, #ff0033 0%, #e6002e 50%, #ff4d6d 100%);
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 10px;
            cursor: pointer;
            z-index: 999999;
            color: #ffffff;
            font-family: 'YouTube Sans', Roboto, Inter, system-ui, sans-serif;
            font-weight: 600;
            font-size: 14px;
            letter-spacing: 0.3px;
            box-shadow: 0 8px 24px rgba(255, 0, 51, 0.45);
            border: 1px solid rgba(255, 255, 255, 0.25);
            backdrop-filter: blur(12px);
            transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
            animation: yt-ai-pulse 3.5s infinite ease-in-out;
            user-select: none;
        }

        .yt-ai-fab:hover {
            transform: translateY(-4px) scale(1.05);
            box-shadow: 0 14px 35px rgba(255, 0, 51, 0.65), 0 0 20px rgba(255, 77, 109, 0.5);
            border-color: rgba(255, 255, 255, 0.5);
        }

        .yt-ai-fab:active {
            transform: translateY(0) scale(0.96);
        }

        .yt-ai-fab-icon {
            display: flex;
            align-items: center;
            justify-content: center;
            width: 24px;
            height: 24px;
            filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.25));
        }

        .yt-ai-fab-text {
            white-space: nowrap;
            text-shadow: 0 1px 2px rgba(0,0,0,0.3);
        }

        .yt-ai-badge {
            background: rgba(255, 255, 255, 0.2);
            padding: 2px 6px;
            border-radius: 8px;
            font-size: 10px;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            border: 1px solid rgba(255, 255, 255, 0.3);
        }
    `;
    document.head.appendChild(style);

    // 2. Inject Container & Modern Pill Button
    const container = document.createElement("div");
    container.id = "youtube-ai-fab-container";

    container.innerHTML = `
        <div class="yt-ai-fab" role="button" aria-label="Open YouTube AI Assistant">
            <div class="yt-ai-fab-icon">
                <svg width="22" height="22" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M12 2L14.5 9.5L22 12L14.5 14.5L12 22L9.5 14.5L2 12L9.5 9.5L12 2Z" fill="#FFFFFF"/>
                    <path d="M19 2L19.8 4.2L22 5L19.8 5.8L19 8L18.2 5.8L16 5L18.2 4.2L16 2Z" fill="#FFE5E9"/>
                </svg>
            </div>
            <span class="yt-ai-fab-text">YouTube AI</span>
        </div>
    `;

    document.body.appendChild(container);

    const fab = container.querySelector(".yt-ai-fab");

    let sidebarVisible = false;
    let sidebar = null;

    // Helper to open sidebar and hide floating button
    function openSidebar() {
        if (sidebarVisible) return;

        sidebar = document.createElement("iframe");
        sidebar.src = chrome.runtime.getURL("sidebar.html");
        sidebar.id = "youtube-ai-sidebar";

        Object.assign(sidebar.style, {
            position: "fixed",
            top: "0",
            right: "0",
            width: "420px",
            height: "100vh",
            border: "none",
            zIndex: "999998",
            background: "#0f0f0f",
            boxShadow: "-5px 0px 20px rgba(0,0,0,0.5)"
        });

        document.body.appendChild(sidebar);
        sidebarVisible = true;

        // Hide floating button when sidebar is open
        fab.style.display = "none";
    }

    // Helper to close sidebar and restore floating button
    function closeSidebar() {
        const existingSidebar = document.getElementById("youtube-ai-sidebar");
        if (existingSidebar) {
            existingSidebar.remove();
        }
        sidebar = null;
        sidebarVisible = false;

        // Show floating button when sidebar is closed
        fab.style.display = "flex";
    }

    fab.addEventListener("click", () => {
        if (!sidebarVisible) {
            openSidebar();
        } else {
            closeSidebar();
        }
    });

    // Listen for close message from iframe sidebar.js
    window.addEventListener("message", (event) => {
        if (event.data && event.data.type === "CLOSE_AI_SIDEBAR") {
            closeSidebar();
        }
    });
}
