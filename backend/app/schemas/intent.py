from typing import Literal

from pydantic import BaseModel, Field


Intent = Literal[
    "order_not_received",
    "payment_failed",
    "payment_success_order_missing",
    "account_login_problem",
    "password_reset",
    "delivery_delay",
    "human_agent_request",
    "unknown",
]

Category = Literal["orders", "payments", "accounts", "delivery", "general"]
Priority = Literal["low", "medium", "high", "urgent"]


class IntentResult(BaseModel):
    intent: Intent
    category: Category
    confidence: float = Field(ge=0, le=1)
    priority: Priority
    reasoning_summary: str

