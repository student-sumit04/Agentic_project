from uuid import uuid4

from app.graph.builder import run_support_workflow
from app.graph.state import SupportState
from app.schemas.api import AgentResponse, ChatMessage, RuntimeInfo, TicketSummary
from app.security.redaction import redact_sensitive_text


class TicketStore:
    def __init__(self) -> None:
        self._tickets: dict[str, SupportState] = {}

    def create_ticket(self, customer_id: str, subject: str) -> TicketSummary:
        ticket_id = f"TCK-{uuid4().hex[:8].upper()}"
        state: SupportState = {
            "ticket_id": ticket_id,
            "customer_id": customer_id,
            "subject": subject,
            "messages": [],
            "resolution_status": "unknown",
            "attempted_steps": [],
            "retry_count": 0,
        }
        self._tickets[ticket_id] = state
        return self.summarize(state)

    def list_tickets(self) -> list[TicketSummary]:
        return [self.summarize(ticket) for ticket in self._tickets.values()]

    def get_ticket_state(self, ticket_id: str) -> SupportState | None:
        return self._tickets.get(ticket_id)

    def add_customer_message(self, customer_id: str, message: str, ticket_id: str | None = None) -> AgentResponse:
        safe_message = redact_sensitive_text(message)
        if ticket_id and ticket_id in self._tickets:
            state = self._tickets[ticket_id]
        else:
            summary = self.create_ticket(customer_id=customer_id, subject=safe_message[:80])
            state = self._tickets[summary.ticket_id]

        state["latest_user_message"] = safe_message
        state["messages"] = state.get("messages", []) + [{"role": "customer", "content": safe_message}]
        next_state = run_support_workflow(state)

        assistant_message = next_state.get("final_answer", "I need a little more information to continue.")
        next_state["messages"] = next_state.get("messages", []) + [{"role": "assistant", "content": assistant_message}]

        ticket_id = next_state["ticket_id"]
        self._tickets[ticket_id] = next_state
        return self._agent_response(next_state)

    def get_messages(self, ticket_id: str) -> list[ChatMessage]:
        state = self._tickets[ticket_id]
        return [ChatMessage(**message) for message in state.get("messages", [])]

    def summarize(self, state: SupportState) -> TicketSummary:
        status = state.get("resolution_status", "unknown")
        if status == "unknown" or status == "unresolved":
            ticket_status = "open"
        elif status == "waiting_for_customer":
            ticket_status = "waiting_for_customer"
        elif status == "resolved":
            ticket_status = "resolved"
        else:
            ticket_status = "escalated"

        return TicketSummary(
            ticket_id=state["ticket_id"],
            customer_id=state["customer_id"],
            subject=state.get("subject", "Support request"),
            status=ticket_status,
            priority=state.get("priority", "medium"),
            intent=state.get("intent"),
        )

    def _agent_response(self, state: SupportState) -> AgentResponse:
        plan = state.get("troubleshooting_plan", [])
        index = state.get("current_step_index", 0)
        current_step = plan[index] if plan and index < len(plan) else None

        fallback_reasons = [state.get("llm_error"), state.get("retrieval_error")]
        return AgentResponse(
            ticket=self.summarize(state),
            assistant_message=state.get("final_answer", ""),
            intent={
                "intent": state.get("intent", "unknown"),
                "category": state.get("category", "general"),
                "confidence": state.get("confidence", 0),
                "priority": state.get("priority", "low"),
                "reasoning_summary": state.get("reasoning_summary", ""),
            },
            entities=state.get("extracted_entities", {}),
            missing_fields=state.get("missing_fields", []),
            retrieved_documents=state.get("retrieved_documents", []),
            current_step=current_step,
            attempted_steps=state.get("attempted_steps", []),
            resolution_status=state.get("resolution_status", "unknown"),
            escalation_summary=state.get("escalation_summary"),
            runtime=RuntimeInfo(
                language_model="groq" if state.get("llm_used") else "deterministic",
                model=state.get("llm_model"),
                retrieval=state.get("retrieval_engine", "keyword"),
                fallback_reason="; ".join(reason for reason in fallback_reasons if reason) or None,
            ),
        )


ticket_store = TicketStore()
