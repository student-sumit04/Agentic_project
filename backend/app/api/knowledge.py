from fastapi import APIRouter

from app.rag.retriever import DOCUMENTS

router = APIRouter(prefix="/knowledge", tags=["knowledge"])


@router.get("")
def list_knowledge_documents() -> list[dict]:
    return [{key: value for key, value in doc.items() if key != "content"} for doc in DOCUMENTS]
