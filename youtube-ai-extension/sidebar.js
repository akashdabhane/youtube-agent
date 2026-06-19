const button =
    document.getElementById("askBtn");

button.addEventListener(
    "click",
    async () => {

        const query =
            document.getElementById("question").value;

        const [tab] =
            await chrome.tabs.query({
                active: true,
                currentWindow: true
            });

        const url = tab.url;

        const response =
            await fetch(
                "http://localhost:8000/chat",
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body: JSON.stringify({
                        query: `
            Current video:
            ${url}

            User Question:
            ${query}
            `
                    })
                }
            );

        const data =
            await response.json();

        document.getElementById(
            "response"
        ).innerText =
            data.response;
    }
);


document
    .getElementById("closeSidebar")
    .addEventListener(
        "click",
        () => {

            window.parent.postMessage(
                {
                    type: "CLOSE_AI_SIDEBAR"
                },
                "*"
            );
        }
    );

