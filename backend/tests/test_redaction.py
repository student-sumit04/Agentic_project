from app.security.redaction import redact_sensitive_text
from app.services.ticket_service import TicketStore


def test_password_value_is_removed_without_losing_warning_context() -> None:
    redacted = redact_sensitive_text("My password is secret123 and login is failing")

    assert "secret123" not in redacted
    assert "My password is [REDACTED]" in redacted


def test_sensitive_message_is_redacted_and_escalated_through_ticket_store() -> None:
    store = TicketStore()

    response = store.add_customer_message(
        customer_id="CUST-1",
        message="My OTP is 482901 and I cannot sign in.",
    )
    history = store.get_messages(response.ticket.ticket_id)

    assert response.resolution_status == "escalated"
    assert "482901" not in history[0].content
    assert "[REDACTED]" in history[0].content
