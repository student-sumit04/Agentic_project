from app.graph.state import SupportState


RESOLVED_TERMS = ["solved", "fixed", "working", "i can see", "received", "yes it worked"]
FAILED_TERMS = ["not solved", "still", "did not", "doesn't", "failed", "no order", "not working"]


def check_resolution(state: SupportState) -> dict:
    message = state.get("latest_user_message", "").lower()
    attempted = [step.copy() for step in state.get("attempted_steps", [])]

    if not attempted or attempted[-1].get("outcome") != "waiting":
        return {"resolution_status": "unknown"}

    if any(term in message for term in FAILED_TERMS):
        outcome = "failed"
        status = "unresolved"
        final_answer = ""
    elif any(term in message for term in RESOLVED_TERMS):
        outcome = "resolved"
        status = "resolved"
        final_answer = "Great, I am glad this is resolved. I will mark the ticket as resolved."
    else:
        outcome = "unclear"
        status = "waiting_for_customer"
        final_answer = "Thanks. Did that step solve the original issue?"

    attempted[-1] = attempted[-1] | {"customer_result": state.get("latest_user_message"), "outcome": outcome}
    return {
        "attempted_steps": attempted,
        "resolution_status": status,
        "final_answer": final_answer,
    }
