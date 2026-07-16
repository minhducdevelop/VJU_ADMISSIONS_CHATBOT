import json
import logging
from datetime import datetime
from typing import Generator, List, Dict, Optional

import redis
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker, Session

from src.config import settings

logger = logging.getLogger("admissions_chatbot.database")
logging.basicConfig(level=logging.INFO)

# ==========================================
# 1. DATABASE LAYER (SQLAlchemy)
# ==========================================
# Create engine (works with SQLite, MySQL, and PostgreSQL/Supabase)
# SQLite needs check_same_thread=False for FastAPI concurrency
connect_args = {}
if settings.DATABASE_URL.startswith("sqlite"):
    connect_args["check_same_thread"] = False

engine = create_engine(settings.DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class ChatLog(Base):
    __tablename__ = "chat_logs"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(100), index=True, nullable=False)
    user_query = Column(Text, nullable=False)
    bot_response = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)

def init_db():
    """Initializes the database schema."""
    logger.info("Initializing relational database schema...")
    Base.metadata.create_all(bind=engine)

def get_db() -> Generator[Session, None, None]:
    """Dependency to get the database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ==========================================
# 2. CACHE LAYER (Redis / Upstash / In-Memory Fallback)
# ==========================================
class SessionHistoryManager:
    """Manages chat history per session using Redis or In-Memory fallback."""
    def __init__(self):
        self.redis_client: Optional[redis.Redis] = None
        self.in_memory_db: Dict[str, List[Dict[str, str]]] = {}
        
        if settings.REDIS_URL:
            try:
                logger.info(f"Connecting to Redis at: {settings.REDIS_URL}")
                self.redis_client = redis.Redis.from_url(
                    settings.REDIS_URL, 
                    decode_responses=True,
                    socket_connect_timeout=5
                )
                # Test connection
                self.redis_client.ping()
                logger.info("Successfully connected to Redis cache database.")
            except Exception as e:
                logger.error(f"Failed to connect to Redis: {e}. Falling back to in-memory history storage.")
                self.redis_client = None
        else:
            logger.info("REDIS_URL not configured. Running with in-memory session history storage.")

    def _get_key(self, session_id: str) -> str:
        return f"chat_history:{session_id}"

    def get_history(self, session_id: str) -> List[Dict[str, str]]:
        """
        Retrieves the last 6 messages (corresponding to 3 user-bot interaction turns).
        Returns a list of dicts, e.g. [{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}]
        """
        if self.redis_client:
            try:
                data = self.redis_client.get(self._get_key(session_id))
                if data:
                    return json.loads(data)
            except Exception as e:
                logger.error(f"Error fetching history from Redis: {e}")
        
        # Fallback/Default to In-Memory
        return self.in_memory_db.get(session_id, [])

    def add_message(self, session_id: str, role: str, content: str):
        """
        Adds a message to the session history.
        Limits the history to the 6 most recent messages (3 turns).
        """
        history = self.get_history(session_id)
        history.append({"role": role, "content": content})
        
        # Keep only the last 6 messages (3 turns)
        if len(history) > 6:
            history = history[-6:]
            
        if self.redis_client:
            try:
                # Store with 24 hours (86400 seconds) expiration to free up space
                self.redis_client.set(
                    self._get_key(session_id), 
                    json.dumps(history),
                    ex=86400
                )
                return
            except Exception as e:
                logger.error(f"Error storing history to Redis: {e}")
                
        # Store in-memory
        self.in_memory_db[session_id] = history

# Instantiate global history manager
history_manager = SessionHistoryManager()
