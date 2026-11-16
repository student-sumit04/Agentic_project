from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import agents, knowledge, messages, tickets
from app.config import get_settings
from app.services.llm_service import get_groq_model

settings = get_settings()

app = FastAPI(title=settings.app_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(tickets.router)
app.include_router(messages.router)
app.include_router(agents.router)
app.include_router(knowledge.router)


@app.get("/health")
def health_check() -> dict:
    return {
        "status": "ok",
        "service": settings.app_name,
        "integrations": {
            "orchestration": "langgraph",
            "groq_configured": get_groq_model() is not None,
            "groq_model": settings.groq_model,
            "vector_store": "chroma",
        },
    }
