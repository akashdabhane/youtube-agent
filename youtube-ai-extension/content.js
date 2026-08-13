if (!document.getElementById("youtube-ai-fab-container")) {

    const container = document.createElement("div");
    container.id = "youtube-ai-fab-container";

    container.innerHTML = `
        <div class="yt-ai-fab">
            🤖
        </div>
    `;

    document.body.appendChild(container);

    const fab = container.querySelector(".yt-ai-fab");

    Object.assign(fab.style, {
        position: "fixed",
        right: "25px",
        bottom: "75px",
        width: "60px",
        height: "60px",
        borderRadius: "50%",
        background: "linear-gradient(135deg, #ff0033, #ff4d6d)",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        fontSize: "24px",
        cursor: "pointer",
        zIndex: "999999",
        boxShadow: "0 10px 30px rgba(255, 0, 51, .4)",
        transition: "transform 0.2s, opacity 0.2s"
    });

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
