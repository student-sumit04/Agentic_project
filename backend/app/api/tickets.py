from fastapi import APIRouter, HTTPException

from app.schemas.api import TicketCreateRequest, TicketSummary
from app.services.ticket_service import ticket_store

router = APIRouter(prefix="/tickets", tags=["tickets"])


@router.post("", response_model=TicketSummary)
def create_ticket(payload: TicketCreateRequest) -> TicketSummary:
    return ticket_store.create_ticket(customer_id=payload.customer_id, subject=payload.subject)


@router.get("", response_model=list[TicketSummary])
def list_tickets() -> list[TicketSummary]:
    return ticket_store.list_tickets()


@router.get("/{ticket_id}", response_model=TicketSummary)
def get_ticket(ticket_id: str) -> TicketSummary:
    state = ticket_store.get_ticket_state(ticket_id)
    if not state:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return ticket_store.summarize(state)
