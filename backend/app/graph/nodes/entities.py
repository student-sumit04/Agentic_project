import re

from app.graph.state import SupportState
from app.schemas.entities import ExtractedIssueData


def extract_entities(state: SupportState) -> dict:
    message = state.get("latest_user_message", "")
    existing = state.get("extracted_entities", {})

    order_id = _first_match(r"\b(?:order|ord)[-\s#:]*(\d{3,})\b", message, re.IGNORECASE)
    transaction_id = _first_match(r"\b(?:txn|transaction)[-\s#:]?([A-Z0-9-]{4,})\b", message, re.IGNORECASE)
    email = _first_match(r"[\w.+-]+@[\w-]+\.[\w.-]+", message)
    date_hint = _first_match(r"\b(today|yesterday|last night|this morning|\d{4}-\d{2}-\d{2})\b", message, re.IGNORECASE)

    payment_method = None
    for candidate in ["upi", "card", "netbanking", "wallet"]:
        if candidate in message.lower():
            payment_method = candidate.upper() if candidate == "upi" else candidate

    data = ExtractedIssueData(
        order_id=order_id or existing.get("order_id"),
        transaction_id=transaction_id or existing.get("transaction_id"),
        account_email=email or existing.get("account_email"),
        issue_start_date=date_hint or existing.get("issue_start_date"),
        payment_method=payment_method or existing.get("payment_method"),
        platform=("web" if "website" in message.lower() else None) or existing.get("platform"),
        error_message=(message if "error" in message.lower() else None) or existing.get("error_message"),
    )
    return {"extracted_entities": data.model_dump()}


def _first_match(pattern: str, text: str, flags: int = 0) -> str | None:
    match = re.search(pattern, text, flags)
    if not match:
        return None
    return match.group(1) if match.groups() else match.group(0)
