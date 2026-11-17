from app.graph.state import SupportState

HIGH_RISK_TERMS = [
    "fraud",
    "legal notice",
    "lawsuit",
    "hacked",
    "account takeover",
    "self harm",
]

SENSITIVE_DATA_PATTERNS = [
    "my otp is",
    "my password is",
    "my cvv is",
    "card number is",
]


def detect_safety_and_urgency(state: SupportState) -> dict:
    message = state.get("latest_user_message", "").lower()
    high_risk = any(term in message for term in HIGH_RISK_TERMS + SENSITIVE_DATA_PATTERNS)
    return {
        "risk_level": "high" if high_risk else "normal",
        "requires_immediate_escalation": high_risk,
        "escalation_reason": "Safety-sensitive or authorization-sensitive request" if high_risk else None,
    }
