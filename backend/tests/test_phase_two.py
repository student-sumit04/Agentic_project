from types import SimpleNamespace

from app.graph.builder import run_support_workflow, support_graph
from app.schemas.entities import ExtractedIssueData
from app.schemas.intent import IntentResult
from app.services import llm_service
from app.services.llm_service import IssueAnalysis
from app.services.ticket_service import TicketStore


def test_workflow_is_compiled_as_langgraph() -> None:
    nodes = support_graph.get_graph().nodes

    assert "analyze_issue" in nodes
    assert "retrieve" in nodes
    assert "respond" in nodes


def test_offline_turn_reports_langgraph_and_deterministic_language() -> None:
    result = run_support_workflow(
        {
            "ticket_id": "TCK-OFFLINE",
            "customer_id": "CUST-1",
            "latest_user_message": "Order 48291 has not arrived.",
            "attempted_steps": [],
        }
    )

    assert result["orchestration_engine"] == "langgraph"
    assert result["llm_used"] is False
    assert result["retrieved_documents"][0]["document_id"] == "DEL-003"


def test_groq_structured_analysis_and_generation_path(monkeypatch) -> None:
    class FakeStructuredModel:
        def invoke(self, _prompt):
            return IssueAnalysis(
                intent=IntentResult(
                    intent="payment_success_order_missing",
                    category="payments",
                    confidence=0.96,
                    priority="high",
                    reasoning_summary="The transfer completed but no order was created.",
                ),
                entities=ExtractedIssueData(
                    transaction_id="BANKREF77",
                    issue_start_date="yesterday",
                    payment_method="bank transfer",
                ),
            )

    class FakeGroqModel:
        def with_structured_output(self, schema):
            assert schema is IssueAnalysis
            return FakeStructuredModel()

        def invoke(self, _messages):
            return SimpleNamespace(content="Please confirm that you are signed in to the account used for payment.")

    monkeypatch.setattr(llm_service, "get_groq_model", lambda: FakeGroqModel())
    store = TicketStore()
    response = store.add_customer_message(
        customer_id="CUST-1",
        message="My bank transfer completed yesterday but the purchase never appeared. Reference BANKREF77.",
    )

    assert response.runtime.language_model == "groq"
    assert response.runtime.orchestration == "langgraph"
    assert response.intent.intent == "payment_success_order_missing"
    assert response.entities.transaction_id == "BANKREF77"
    assert "account used for payment" in response.assistant_message
