from fastapi import APIRouter, HTTPException

from app.schemas.api import AgentResponse, ChatMessage, CustomerMessageRequest
from app.services.ticket_service import ticket_store

router = APIRouter(prefix="/messages", tags=["messages"])


@router.post("", response_model=AgentResponse)
def send_message(payload: CustomerMessageRequest) -> AgentResponse:
    return ticket_store.add_customer_message(
        ticket_id=payload.ticket_id,
        customer_id=payload.customer_id,
        message=payload.message,
    )


@router.get("/{ticket_id}", response_model=list[ChatMessage])
def list_messages(ticket_id: str) -> list[ChatMessage]:
    if not ticket_store.get_ticket_state(ticket_id):
        raise HTTPException(status_code=404, detail="Ticket not found")
    return ticket_store.get_messages(ticket_id)

