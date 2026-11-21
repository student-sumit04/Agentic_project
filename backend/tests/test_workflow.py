from app.graph.builder import run_support_workflow


def test_payment_issue_asks_for_missing_transaction_date() -> None:
    state = {
        "ticket_id": "TCK-1",
        "customer_id": "CUST-1",
        "latest_user_message": "I paid but my order is not showing.",
        "attempted_steps": [],
    }

    result = run_support_workflow(state)

    assert result["intent"] == "payment_success_order_missing"
    assert result["resolution_status"] == "waiting_for_customer"
    assert "transaction ID" in result["final_answer"]


def test_payment_issue_with_details_presents_one_step() -> None:
    state = {
        "ticket_id": "TCK-2",
        "customer_id": "CUST-1",
        "latest_user_message": "Paid through UPI yesterday, transaction TXN8892, but order is not showing.",
        "attempted_steps": [],
    }

    result = run_support_workflow(state)

    assert result["retrieved_documents"][0]["document_id"] == "PAY-004"
    assert result["attempted_steps"][0]["step_id"] == "pay-account-match"
    assert result["resolution_status"] == "waiting_for_customer"


def test_regular_password_reset_request_is_not_treated_as_high_risk() -> None:
    state = {
        "ticket_id": "TCK-3",
        "customer_id": "CUST-1",
        "latest_user_message": "I cannot login and need to reset my password. Email is me@example.com.",
        "attempted_steps": [],
    }

    result = run_support_workflow(state)

    assert result["intent"] == "account_login_problem"
    assert result["resolution_status"] == "waiting_for_customer"
    assert result["attempted_steps"][0]["step_id"] == "acc-reset"


def test_customer_sharing_a_password_is_escalated() -> None:
    state = {
        "ticket_id": "TCK-4",
        "customer_id": "CUST-1",
        "latest_user_message": "My password is secret123 and I cannot login.",
        "attempted_steps": [],
    }

    result = run_support_workflow(state)

    assert result["resolution_status"] == "escalated"
    assert result["requires_immediate_escalation"] is True


def test_delivery_message_uses_natural_customer_wording() -> None:
    state = {
        "ticket_id": "TCK-5",
        "customer_id": "CUST-1",
        "latest_user_message": "Order 48291 was due yesterday but has not arrived.",
        "attempted_steps": [],
    }

    result = run_support_workflow(state)

    assert result["intent"] == "delivery_delay"
    assert result["retrieved_documents"][0]["document_id"] == "DEL-003"
    assert result["attempted_steps"][0]["step_id"] == "del-tracking"
