from app.graph.state import SupportState


def escalate_case(state: SupportState) -> dict:
    attempted = state.get("attempted_steps", [])
    steps = "\n".join(
        f"- {step.get('title')}: {step.get('outcome', 'waiting')}" for step in attempted
    ) or "- No troubleshooting steps completed"

    summary = (
        f"Issue: {state.get('intent', 'unknown')}\n"
        f"Customer: {state.get('customer_id', 'unknown')}\n"
        f"Ticket: {state.get('ticket_id', 'unknown')}\n"
        f"Reason: {state.get('escalation_reason') or 'Human review requested'}\n"
        f"Steps attempted:\n{steps}\n"
        f"Recommended action: Review ticket context and verify account/order/payment data in internal tools."
    )

    return {
        "resolution_status": "escalated",
        "escalation_summary": summary,
        "final_answer": "I am escalating this to a human support agent with the details collected so far.",
    }

