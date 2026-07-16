import os
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv

# Load env variables explicitly just in case
load_dotenv()

class Settings(BaseSettings):
    # Google Gemini API Key - required for embedding and generation
    GEMINI_API_KEY: Optional[str] = None
    
    # Database connection URL: SQLite (default), MySQL or Supabase (PostgreSQL)
    DATABASE_URL: str = "sqlite:///./admissions_chatbot.db"
    
    # Redis URL for session storage (Upstash Redis or local). 
    # If not provided, the server will fallback to in-memory dictionary.
    REDIS_URL: Optional[str] = None
    
    # Path where local ChromaDB stores the vectors
    CHROMA_DB_DIR: str = "./chroma_db"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()

# Validate API key presence and warn if missing
if not settings.GEMINI_API_KEY:
    print("WARNING: GEMINI_API_KEY is not set in environment or .env file. "
          "Please configure it to use embeddings and the Gemini model.")
