from fastapi import APIRouter, HTTPException

from app.services.ticket_service import ticket_store

router = APIRouter(prefix="/agents", tags=["agents"])


@router.get("/escalations")
def list_escalations() -> list[dict]:
    escalated = []
    for ticket in ticket_store.list_tickets():
        if ticket.status == "escalated":
            state = ticket_store.get_ticket_state(ticket.ticket_id)
            escalated.append({"ticket": ticket, "summary": state.get("escalation_summary") if state else None})
    return escalated


@router.post("/tickets/{ticket_id}/resolve")
def resolve_ticket(ticket_id: str) -> dict:
    state = ticket_store.get_ticket_state(ticket_id)
    if not state:
        raise HTTPException(status_code=404, detail="Ticket not found")
    state["resolution_status"] = "resolved"
    return {"ticket_id": ticket_id, "status": "resolved"}

