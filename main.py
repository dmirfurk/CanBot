from fastapi import FastAPI
from pydantic import BaseModel
from nlp.router import route_question
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Erzincan Belediyesi Akıllı Chatbot API",
    version="1.0.0"
)

# CORS ayarları
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    question: str

class ChatResponse(BaseModel):
    answer: str
    items: list = []

@app.get("/")
def read_root():
    return {"status": "active", "message": "Chatbot API çalışıyor."}

@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    # route_question fonksiyonu artık dictionary dönüyor
    response_data = route_question(req.question)
    return response_data