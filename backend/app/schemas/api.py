from typing import Literal

from pydantic import BaseModel, Field

from app.schemas.entities import ExtractedIssueData
from app.schemas.intent import IntentResult
from app.schemas.troubleshooting import AttemptedStep, TroubleshootingStep


class CustomerMessageRequest(BaseModel):
    ticket_id: str | None = None
    customer_id: str = "CUST-DEMO"
    message: str = Field(min_length=1, max_length=4000)


class TicketCreateRequest(BaseModel):
    customer_id: str = "CUST-DEMO"
    subject: str = Field(min_length=1, max_length=140)


class ChatMessage(BaseModel):
    role: Literal["customer", "assistant", "agent", "system"]
    content: str


class RetrievedDocument(BaseModel):
    document_id: str
    title: str
    category: str
    score: float
    snippet: str


class TicketSummary(BaseModel):
    ticket_id: str
    customer_id: str
    subject: str
    status: Literal["open", "waiting_for_customer", "resolved", "escalated"]
    priority: Literal["low", "medium", "high", "urgent"] = "medium"
    intent: str | None = None


class RuntimeInfo(BaseModel):
    orchestration: Literal["langgraph"] = "langgraph"
    language_model: Literal["groq", "deterministic"]
    model: str | None = None
    retrieval: Literal["chroma", "keyword"]
    fallback_reason: str | None = None


class AgentResponse(BaseModel):
    ticket: TicketSummary
    assistant_message: str
    intent: IntentResult
    entities: ExtractedIssueData
    missing_fields: list[str]
    retrieved_documents: list[RetrievedDocument]
    current_step: TroubleshootingStep | None = None
    attempted_steps: list[AttemptedStep]
    resolution_status: Literal["unknown", "waiting_for_customer", "resolved", "unresolved", "escalated"]
    escalation_summary: str | None = None
    runtime: RuntimeInfo
