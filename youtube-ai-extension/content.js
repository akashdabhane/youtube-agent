if (!document.getElementById("youtube-ai-btn")) {

    const button =
        document.createElement("div");

    button.innerHTML = `
<div class="yt-ai-fab">
 🤖
</div>
`;

    document.body.appendChild(button);

    const fab =
        button.querySelector(".yt-ai-fab");

    Object.assign(fab.style, {
        position: "fixed",
        right: "25px",
        bottom: "75px",

        width: "65px",
        height: "65px",

        borderRadius: "50%",

        background:
            "linear-gradient(135deg,#ff0033,#ff4d6d)",

        display: "flex",
        alignItems: "center",
        justifyContent: "center",

        fontSize: "24px",

        cursor: "pointer",

        zIndex: "999999",

        boxShadow:
            "0 10px 30px rgba(255,0,51,.4)"
    });

    document.body.appendChild(button);

    let sidebarVisible = false;
    let sidebar = null;

    button.addEventListener("click", () => {

        if (!sidebarVisible) {

            sidebar = document.createElement("iframe");

            sidebar.src =
                chrome.runtime.getURL("sidebar.html");

            sidebar.id = "youtube-ai-sidebar";

            Object.assign(sidebar.style, {
                position: "fixed",
                top: "0",
                right: "0",
                width: "450px",
                height: "100vh",
                border: "none",
                zIndex: "999998",
                background: "white",
                boxShadow: "-3px 0px 10px rgba(0,0,0,0.2)"
            });

            document.body.appendChild(sidebar);

            sidebarVisible = true;

        } else {

            sidebar.remove();

            sidebarVisible = false;
        }
    });
}

window.addEventListener(
    "message",
    (event) => {

        if (
            event.data.type ===
            "CLOSE_AI_SIDEBAR"
        ) {

            const sidebar =
                document.getElementById(
                    "youtube-ai-sidebar"
                );

            if (sidebar) {
                sidebar.remove();
            }
        }
    }
);

