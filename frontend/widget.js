async function sendMessage() {
    const input = document.getElementById("userInput");
    const message = input.value.trim();
    if (!message) return;

    addMessage("Sen", message, "user");
    input.value = "";

    try {
        const response = await fetch("http://127.0.0.1:8000/chat", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ question: message })
        });

        const data = await response.json();
        addMessage("CanBot", data.answer || "Cevap yok", "bot");

    } catch (error) {
        addMessage("Hata", "Backend'e baðlanýlamadý", "bot");
        console.error(error);
    }
}

function addMessage(sender, text, className) {
    const chatBox = document.getElementById("chat-box");
    const div = document.createElement("div");
    div.className = `message ${className}`;
    div.innerHTML = `<strong>${sender}:</strong> ${text}`;
    chatBox.appendChild(div);
    chatBox.scrollTop = chatBox.scrollHeight;
}
