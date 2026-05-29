from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional

# Import our custom logic
from backend.auth import authenticate_user, LoginRequest, UserResponse
from backend.rag_engine import get_answer

app = FastAPI(title="RBAC Enterprise Chatbot API")

# Pydantic models for the /chat endpoint
class ChatRequest(BaseModel):
    query: str
    role: str
    chat_history: list = []

class ChatResponse(BaseModel):
    answer: str

@app.post("/login", response_model=UserResponse)
def login(request: LoginRequest):
    """
    Endpoint for users to log in. Returns their role if successful.
    """
    user = authenticate_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    return user

@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    """
    Endpoint to process a chat message. 
    It takes the query and the user's role, and returns the RAG answer.
    """
    try:
        # Pass the query, role, and chat history to our RAG engine
        answer = get_answer(request.query, request.role, request.chat_history)
        return ChatResponse(answer=answer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
