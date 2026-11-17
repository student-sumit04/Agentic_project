from app.graph.state import SupportState


REQUIRED_FIELDS = {
    "payment_success_order_missing": ["transaction_id", "issue_start_date"],
    "payment_failed": ["transaction_id", "issue_start_date"],
    "delivery_delay": ["order_id"],
    "account_login_problem": ["account_email"],
}


FIELD_LABELS = {
    "transaction_id": "transaction ID",
    "issue_start_date": "when the issue started",
    "order_id": "order ID",
    "account_email": "account email",
}


def check_missing_information(state: SupportState) -> dict:
    intent = state.get("intent", "unknown")
    entities = state.get("extracted_entities", {})
    required = REQUIRED_FIELDS.get(intent, [])
    missing = [field for field in required if not entities.get(field)]
    return {"missing_fields": missing}


def ask_for_information(state: SupportState) -> dict:
    labels = [FIELD_LABELS.get(field, field.replace("_", " ")) for field in state.get("missing_fields", [])]
    if not labels:
        return {}

    if len(labels) == 1:
        question = f"Please share your {labels[0]} so I can check the right support path."
    else:
        question = f"Please share your {', '.join(labels[:-1])} and {labels[-1]} so I can check the right support path."

    return {
        "resolution_status": "waiting_for_customer",
        "final_answer": question,
    }

