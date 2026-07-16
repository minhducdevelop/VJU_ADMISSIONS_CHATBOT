import logging
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from typing import List

from src.config import settings
from src.database import get_db, init_db, ChatLog
from src.rag_engine import rag_engine

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("admissions_chatbot.main")

# Create FastAPI app instance
app = FastAPI(
    title="AI Admissions Assistant API",
    description="RAG-based conversational AI for Vietnam Japan University (VJU) admissions inquiries.",
    version="1.0.0"
)

# CORS configurations (useful for frontend integrations)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic schemas
class ChatRequest(BaseModel):
    user_query: str = Field(..., description="The query/question from the candidate.", example="Học phí ngành Máy tính là bao nhiêu?")
    session_id: str = Field(..., description="Unique conversation session ID to track history.", example="session_user_99")

class ChatResponse(BaseModel):
    session_id: str
    answer: str

class ChatLogSchema(BaseModel):
    id: int
    session_id: str
    user_query: str
    bot_response: str
    timestamp: str

    class Config:
        from_attributes = True

# Startup Event: Create DB tables if they don't exist
@app.on_event("startup")
def startup_event():
    logger.info("Starting up AI Admissions Assistant server...")
    try:
        init_db()
        logger.info("Database schema initialized successfully.")
    except Exception as e:
        logger.error(f"Error during database initialization: {e}")

# Endpoints
@app.get("/health", tags=["Status"])
def health_check():
    """Returns the API service health status."""
    return {"status": "healthy", "service": "VJU Admissions Assistant"}

@app.post("/chat", response_model=ChatResponse, tags=["Chat"])
def chat(request: ChatRequest, db: Session = Depends(get_db)):
    """
    Main chat endpoint. Processes queries using RAG, logs interactions in the SQL database, 
    and saves conversation state in Redis.
    """
    user_query = request.user_query.strip()
    session_id = request.session_id.strip()

    if not user_query:
        raise HTTPException(status_code=400, detail="User query cannot be empty.")
    if not session_id:
        raise HTTPException(status_code=400, detail="Session ID cannot be empty.")

    # 1. Get answer from RAG engine
    try:
        answer = rag_engine.query(session_id=session_id, user_query=user_query)
    except Exception as e:
        logger.error(f"RAG Engine error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error processing query in the AI engine."
        )

    # 2. Log interaction to SQL DB (MySQL / Supabase / SQLite)
    try:
        chat_log = ChatLog(
            session_id=session_id,
            user_query=user_query,
            bot_response=answer
        )
        db.add(chat_log)
        db.commit()
        logger.info(f"Logged chat interaction for session: {session_id} to database.")
    except Exception as e:
        # Non-blocking log error so the candidate still receives the response
        logger.error(f"Database logging failed: {e}")
        db.rollback()

    return ChatResponse(session_id=session_id, answer=answer)

@app.get("/history/{session_id}", response_model=List[ChatLogSchema], tags=["Admins"])
def get_session_history(session_id: str, db: Session = Depends(get_db)):
    """
    Retrieves full persistent chat logs for a specific session ID from the SQL database.
    (Mainly used by admins for monitoring and analysis).
    """
    try:
        logs = db.query(ChatLog).filter(ChatLog.session_id == session_id).order_by(ChatLog.timestamp.asc()).all()
        # Convert timestamp to ISO format string for response compatibility
        response_logs = []
        for log in logs:
            response_logs.append(ChatLogSchema(
                id=log.id,
                session_id=log.session_id,
                user_query=log.user_query,
                bot_response=log.bot_response,
                timestamp=log.timestamp.isoformat()
            ))
        return response_logs
    except Exception as e:
        logger.error(f"Failed to retrieve history logs: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve history from persistent database."
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True)
