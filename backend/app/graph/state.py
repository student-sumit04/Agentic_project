from typing import Literal, TypedDict


class SupportState(TypedDict, total=False):
    ticket_id: str
    customer_id: str
    subject: str
    messages: list[dict]
    latest_user_message: str
    risk_level: Literal["normal", "high"]
    requires_immediate_escalation: bool
    intent: str
    category: str
    confidence: float
    priority: str
    reasoning_summary: str
    extracted_entities: dict
    missing_fields: list[str]
    retrieved_documents: list[dict]
    retrieval_confidence: float
    troubleshooting_plan: list[dict]
    current_step_index: int
    attempted_steps: list[dict]
    customer_step_result: str
    resolution_status: Literal["unknown", "waiting_for_customer", "resolved", "unresolved", "escalated"]
    retry_count: int
    escalation_reason: str | None
    escalation_summary: str | None
    final_answer: str
    orchestration_engine: Literal["langgraph"]
    llm_used: bool
    llm_model: str | None
    llm_error: str | None
    retrieval_engine: Literal["chroma", "keyword"]
    retrieval_error: str | None
