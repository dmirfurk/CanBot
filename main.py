# -*- coding: utf-8 -*-
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from services.faq_service import load_faq_data
from nlp.faq_matcher import FAQMatcher

from db.database import engine, SessionLocal
from models.log import ChatLog

# ---------------- FASTAPI APP ----------------
app = FastAPI(
    title="Erzincan Belediyesi Akilli Chatbot API",
    description="Erzincan Belediyesi web sitesi icin gelistirilen akilli chatbot sistemi",
    version="1.0"
)

# ---------------- CORS ----------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------- DB TABLES ----------------
ChatLog.metadata.create_all(bind=engine)

# ---------------- FAQ + NLP ----------------
faq_data = load_faq_data()
faq_matcher = FAQMatcher(faq_data)

# ---------------- MODELS ----------------
class ChatRequest(BaseModel):
    question: str


class ChatResponse(BaseModel):
    answer: str
    intent: str | None = None


# ---------------- ENDPOINTS ----------------
@app.get("/")
def root():
    return {"status": "API calisiyor"}


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    result = faq_matcher.find_best_match(request.question)

    if not result:
        answer = "Sorunuzu anlayamadim. Lutfen farkli bir sekilde sorar misiniz?"
        intent = None
    else:
        answer = result["answer"]
        intent = result["intent"]

    # -------- LOG KAYDI --------
    db = SessionLocal()
    log = ChatLog(
        question=request.question,
        answer=answer,
        intent=intent
    )
    db.add(log)
    db.commit()
    db.close()

    return ChatResponse(
        answer=answer,
        intent=intent
    )


print(">>> main.py CALISIYOR (LOG AKTIF) <<<")
