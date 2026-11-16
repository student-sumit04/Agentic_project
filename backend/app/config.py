from functools import lru_cache
import os
from dataclasses import dataclass, field

from dotenv import load_dotenv


load_dotenv()


@dataclass(frozen=True)
class Settings:
    app_name: str = "AI Customer Support Resolution Agent"
    database_url: str = "sqlite:///./support_agent.db"
    vector_db_path: str = "./data/chroma"
    groq_api_key: str = ""
    groq_model: str = "llama-3.3-70b-versatile"
    groq_timeout_seconds: float = 20.0
    jwt_secret: str = "replace_with_long_random_secret"
    max_troubleshooting_attempts: int = 4
    retrieval_top_k: int = 5
    min_retrieval_score: float = 0.6
    cors_origins: list[str] = field(default_factory=lambda: ["http://localhost:5173", "http://localhost:3000"])


@lru_cache
def get_settings() -> Settings:
    return Settings(
        database_url=os.getenv("DATABASE_URL", Settings.database_url),
        vector_db_path=os.getenv("VECTOR_DB_PATH", Settings.vector_db_path),
        groq_api_key=os.getenv("GROQ_API_KEY", ""),
        groq_model=os.getenv("GROQ_MODEL", Settings.groq_model),
        groq_timeout_seconds=float(os.getenv("GROQ_TIMEOUT_SECONDS", "20")),
        jwt_secret=os.getenv("JWT_SECRET", Settings.jwt_secret),
        max_troubleshooting_attempts=int(os.getenv("MAX_TROUBLESHOOTING_ATTEMPTS", "4")),
        retrieval_top_k=int(os.getenv("RETRIEVAL_TOP_K", "5")),
        min_retrieval_score=float(os.getenv("MIN_RETRIEVAL_SCORE", "0.6")),
    )
