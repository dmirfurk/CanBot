const API_URL = "http://127.0.0.1:8000/chat";

// Elementleri Seçelim
const chatContainer = document.getElementById("chat-container");
const chatToggle = document.getElementById("chat-toggle");
const closeChatBtn = document.getElementById("close-chat");
const questionInput = document.getElementById("question");
const sendBtn = document.getElementById("send-btn");
const messagesDiv = document.getElementById("messages");
const toggleIcon = chatToggle.querySelector(".icon");
const toggleCloseIcon = chatToggle.querySelector(".close-icon");

// --- 1. AÇMA / KAPAMA MANTIĞI ---
function toggleChat() {
    // 'active' class'ını ekle/çıkar
    const isActive = chatContainer.classList.toggle("active");

    // İkonu değiştir (Robot <-> Çarpı)
    if (isActive) {
        toggleIcon.style.display = "none";
        toggleCloseIcon.style.display = "block";
        questionInput.focus(); // Açılınca inputa odaklan
    } else {
        toggleIcon.style.display = "block";
        toggleCloseIcon.style.display = "none";
    }
}

// Butona tıklayınca aç/kapa
chatToggle.addEventListener("click", toggleChat);

// Header'daki çizgiye (-) basınca kapat
closeChatBtn.addEventListener("click", () => {
    chatContainer.classList.remove("active");
    toggleIcon.style.display = "block";
    toggleCloseIcon.style.display = "none";
});

// --- 2. MESAJLAŞMA MANTIĞI ---

function addMessage(htmlContent, sender) {
    const div = document.createElement("div");
    div.className = "message " + sender;
    const span = document.createElement("span");
    span.innerHTML = htmlContent;
    div.appendChild(span);
    messagesDiv.appendChild(div);
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
}

async function sendMessage() {
    const text = questionInput.value.trim();
    if (!text) return;

    // Kullanıcı mesajını ekle
    addMessage(text, "user");
    questionInput.value = "";

    // Yükleniyor efekti (Opsiyonel ama şık durur)
    const loadingDiv = document.createElement("div");
    loadingDiv.className = "message bot";
    loadingDiv.innerHTML = "<span>...</span>";
    loadingDiv.id = "loading-msg";
    messagesDiv.appendChild(loadingDiv);
    messagesDiv.scrollTop = messagesDiv.scrollHeight;

    try {
        const res = await fetch(API_URL, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ question: text })
        });

        if (!res.ok) throw new Error("API Hatası");

        const data = await res.json();

        // Yükleniyor mesajını kaldır
        const loadingMsg = document.getElementById("loading-msg");
        if (loadingMsg) loadingMsg.remove();

        // Cevabı hazırla
        let replyHtml = `<div>${data.answer}</div>`;

        if (data.items && data.items.length > 0) {
            data.items.forEach(item => {
                replyHtml += `
                    <a href="${item.url}" target="_blank" class="bot-link">
                        👉 ${item.title}
                    </a>
                `;
            });
        }

        addMessage(replyHtml, "bot");

    } catch (err) {
        const loadingMsg = document.getElementById("loading-msg");
        if (loadingMsg) loadingMsg.remove();
        console.error(err);
        addMessage("⚠️ Üzgünüm, bağlantı hatası oluştu.", "bot");
    }
}

// Gönder butonuna basınca
sendBtn.addEventListener("click", sendMessage);

// Enter tuşuna basınca
questionInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter") sendMessage();
});