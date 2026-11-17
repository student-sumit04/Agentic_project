import hashlib
import logging
import math
import re
from functools import lru_cache
from pathlib import Path

from app.config import get_settings
from app.graph.state import SupportState


KNOWLEDGE_BASE_PATH = Path(__file__).resolve().parents[2] / "knowledge_base"
CATEGORY_BY_PREFIX = {"PAY": "payments", "ACC": "accounts", "DEL": "delivery"}
TOKEN_PATTERN = re.compile(r"[a-z0-9]+")
EMBEDDING_DIMENSIONS = 256
logger = logging.getLogger(__name__)


def load_knowledge_documents() -> list[dict]:
    documents = []
    for path in sorted(KNOWLEDGE_BASE_PATH.glob("*.md")):
        content = path.read_text(encoding="utf-8").strip()
        heading, _, body = content.partition("\n")
        heading = heading.removeprefix("# ").strip()
        document_id, separator, title = heading.partition(":")
        if not separator:
            document_id, title = path.stem, heading
        category = CATEGORY_BY_PREFIX.get(document_id.split("-", 1)[0], "general")
        documents.append(
            {
                "document_id": document_id.strip(),
                "title": title.strip(),
                "category": category,
                "snippet": " ".join(body.split()),
                "content": content,
            }
        )
    return documents


DOCUMENTS = load_knowledge_documents()


class KnowledgeIndex:
    def __init__(self) -> None:
        import chromadb
        from chromadb.config import Settings as ChromaSettings

        settings = get_settings()
        database_path = Path(settings.vector_db_path).resolve()
        database_path.mkdir(parents=True, exist_ok=True)
        client = chromadb.PersistentClient(
            path=str(database_path),
            settings=ChromaSettings(anonymized_telemetry=False),
        )
        self.collection = client.get_or_create_collection(
            name="quickcart_support",
            metadata={"hnsw:space": "cosine"},
        )
        self._upsert_documents()

    def _upsert_documents(self) -> None:
        if not DOCUMENTS:
            return
        self.collection.upsert(
            ids=[doc["document_id"] for doc in DOCUMENTS],
            documents=[doc["content"] for doc in DOCUMENTS],
            embeddings=[embed_text(doc["content"]) for doc in DOCUMENTS],
            metadatas=[
                {
                    "title": doc["title"],
                    "category": doc["category"],
                    "snippet": doc["snippet"],
                }
                for doc in DOCUMENTS
            ],
        )

    def search(self, query: str, category: str, top_k: int) -> list[dict]:
        count = self.collection.count()
        if count == 0:
            return []

        parameters = {
            "query_embeddings": [embed_text(query)],
            "n_results": min(top_k, count),
            "include": ["metadatas", "distances"],
        }
        if category != "general":
            parameters["where"] = {"category": category}

        result = self.collection.query(**parameters)
        ids = result.get("ids", [[]])[0]
        metadatas = result.get("metadatas", [[]])[0]
        distances = result.get("distances", [[]])[0]
        return [
            {
                "document_id": document_id,
                "title": metadata["title"],
                "category": metadata["category"],
                "snippet": metadata["snippet"],
                "score": round(max(0.0, 1.0 - float(distance)), 4),
            }
            for document_id, metadata, distance in zip(ids, metadatas, distances)
        ]


def embed_text(text: str) -> list[float]:
    vector = [0.0] * EMBEDDING_DIMENSIONS
    for token in TOKEN_PATTERN.findall(text.lower()):
        digest = hashlib.sha256(token.encode("utf-8")).digest()
        index = int.from_bytes(digest[:4], "big") % EMBEDDING_DIMENSIONS
        vector[index] += 1.0

    magnitude = math.sqrt(sum(value * value for value in vector))
    return [value / magnitude for value in vector] if magnitude else vector


@lru_cache
def get_knowledge_index() -> KnowledgeIndex:
    return KnowledgeIndex()


def retrieve_knowledge(state: SupportState) -> dict:
    settings = get_settings()
    query = " ".join(
        part
        for part in [
            state.get("latest_user_message", ""),
            state.get("intent", ""),
            state.get("category", ""),
        ]
        if part
    )
    try:
        documents = get_knowledge_index().search(
            query=query,
            category=state.get("category", "general"),
            top_k=settings.retrieval_top_k,
        )
        engine = "chroma"
        retrieval_error = None
    except Exception as exc:
        logger.warning("Chroma retrieval failed; using keyword fallback: %s", exc)
        documents = _keyword_search(query, state.get("category", "general"), settings.retrieval_top_k)
        engine = "keyword"
        retrieval_error = f"{type(exc).__name__}: Chroma unavailable"

    return {
        "retrieved_documents": documents,
        "retrieval_confidence": documents[0]["score"] if documents else 0,
        "retrieval_engine": engine,
        "retrieval_error": retrieval_error,
    }


def _keyword_search(query: str, category: str, top_k: int) -> list[dict]:
    query_tokens = set(TOKEN_PATTERN.findall(query.lower()))
    ranked = []
    for doc in DOCUMENTS:
        document_tokens = set(TOKEN_PATTERN.findall(doc["content"].lower()))
        overlap = len(query_tokens & document_tokens) / max(len(query_tokens), 1)
        category_bonus = 0.35 if doc["category"] == category else 0.0
        ranked.append(
            {key: value for key, value in doc.items() if key != "content"}
            | {"score": round(min(0.98, overlap + category_bonus), 4)}
        )
    ranked.sort(key=lambda item: item["score"], reverse=True)
    return ranked[:top_k]
