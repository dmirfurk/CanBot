from fastapi import FastAPI
from pydantic import BaseModel
from nlp.router import route_question

app = FastAPI(
    title="Erzincan Belediyesi Akilli Chatbot API"
)

class ChatRequest(BaseModel):
    question: str

class ChatResponse(BaseModel):
    answer: str
    items: list = []

@app.post("/chat")
def chat(req: ChatRequest):
    return route_question(req.question)

