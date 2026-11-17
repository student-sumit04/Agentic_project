from app.graph.state import SupportState
from app.schemas.intent import IntentResult


def detect_intent(state: SupportState) -> dict:
    message = state.get("latest_user_message", "").lower()

    if "human" in message or "agent" in message:
        result = IntentResult(
            intent="human_agent_request",
            category="general",
            confidence=0.95,
            priority="high",
            reasoning_summary="Customer explicitly asked for a human agent.",
        )
    elif "login" in message or "sign in" in message or "password" in message:
        result = IntentResult(
            intent="account_login_problem",
            category="accounts",
            confidence=0.82,
            priority="medium",
            reasoning_summary="Message mentions login or password access trouble.",
        )
    elif "paid" in message or "payment" in message or "transaction" in message or "upi" in message:
        if "not showing" in message or "missing" in message or "cannot see" in message:
            intent = "payment_success_order_missing"
        else:
            intent = "payment_failed"
        result = IntentResult(
            intent=intent,
            category="payments",
            confidence=0.84,
            priority="high",
            reasoning_summary="Message describes a payment-related issue.",
        )
    elif any(
        phrase in message
        for phrase in ["delivery", "delayed", "late", "not received", "not arrived", "hasn't arrived"]
    ):
        result = IntentResult(
            intent="delivery_delay",
            category="delivery",
            confidence=0.8,
            priority="medium",
            reasoning_summary="Message describes a delayed or missing delivery.",
        )
    else:
        if state.get("intent") and state.get("intent") != "unknown":
            return {
                "intent": state["intent"],
                "category": state.get("category", "general"),
                "confidence": state.get("confidence", 0.5),
                "priority": state.get("priority", "medium"),
                "reasoning_summary": "Continuing the existing ticket intent from earlier context.",
            }
        result = IntentResult(
            intent="unknown",
            category="general",
            confidence=0.35,
            priority="low",
            reasoning_summary="No supported MVP intent was confidently detected.",
        )

    return result.model_dump()
