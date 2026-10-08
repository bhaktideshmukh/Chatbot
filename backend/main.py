from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

# Import our custom logic
from backend.database import get_db, User
from backend.auth import authenticate_user, LoginRequest, TokenResponse, get_password_hash
from backend.rag_engine import get_answer

app = FastAPI(title="RBAC Enterprise Chatbot API")



class ChatRequest(BaseModel):
    query: str
    role: str
    chat_history: list = []

class ChatResponse(BaseModel):
    answer: str

@app.post("/login", response_model=TokenResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    """
    Endpoint for users to log in. Returns JWT token and role if successful.
    """
    user_token = authenticate_user(db, request)
    if not user_token:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    return user_token

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
