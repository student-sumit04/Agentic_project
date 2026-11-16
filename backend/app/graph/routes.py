from app.graph.state import SupportState


def route_after_safety(state: SupportState) -> str:
    if state.get("requires_immediate_escalation"):
        return "escalate"
    return "detect_intent"


def route_after_missing_check(state: SupportState) -> str:
    if state.get("missing_fields"):
        return "ask_for_information"
    return "retrieve_knowledge"


def route_after_resolution(state: SupportState) -> str:
    status = state.get("resolution_status", "unknown")
    if status == "resolved":
        return "close"
    if status == "escalated":
        return "escalate"
    return "present_step"

