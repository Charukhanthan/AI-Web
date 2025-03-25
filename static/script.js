const wsUrl = (() => {
    const storedUrl = localStorage.getItem("wsUrl");
    return storedUrl || (window.location.protocol === "https:" ? "wss://" + window.location.host + "/ws" : "ws://" + window.location.host + "/ws");
})();

let ws;
function connectWebSocket() {
    ws = new WebSocket(wsUrl);
    ws.onopen = () => {
        console.log("Connected to WebSocket");
        document.getElementById("sendButton").disabled = false;
    };
    ws.onerror = (error) => console.error("WebSocket error", error);
    ws.onclose = () => {
        console.warn("WebSocket connection closed, reconnecting in 3 seconds...");
        document.getElementById("sendButton").disabled = true;
        setTimeout(connectWebSocket, 3000);
    };
    ws.onmessage = (event) => {
        try {
            const data = event.data.trim();
            if (data) {
                document.getElementById("typing-indicator").style.display = "none";
                appendMessage("Bot: " + data, "bot");
            }
        } catch (error) {
            console.error("Error handling message:", error);
        }
    };
}

connectWebSocket();

const messagesContainer = document.getElementById("messages");
const messageInput = document.getElementById("message");
const sendButton = document.getElementById("sendButton");

function appendMessage(text, sender) {
    const messageDiv = document.createElement("div");
    messageDiv.classList.add("message", sender);
    messageDiv.textContent = text;
    messagesContainer.appendChild(messageDiv);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

function sendMessage() {
    const text = messageInput.value.trim();
    if (text && ws.readyState === WebSocket.OPEN) {
        appendMessage("You: " + text, "user");
        document.getElementById("typing-indicator").style.display = "block";
        ws.send(text);
    }
    messageInput.value = "";
    sendButton.disabled = true;
}

// Enable/Disable send button based on input
messageInput.addEventListener("input", () => {
    sendButton.disabled = messageInput.value.trim() === "";
});

// Handle Enter for sending and Shift+Enter for new line
messageInput.addEventListener("keydown", (event) => {
    if (event.key === "Enter") {
        if (event.shiftKey) {
            event.preventDefault(); // Prevent form submission
            messageInput.value += "\n";
        } else {
            event.preventDefault();
            sendMessage();
        }
    }
});

sendButton.addEventListener("click", sendMessage);