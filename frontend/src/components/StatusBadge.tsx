import type { TicketStatus } from "../types/support";

const labels: Record<TicketStatus, string> = {
  open: "Open",
  waiting_for_customer: "Waiting",
  resolved: "Resolved",
  escalated: "Escalated"
};

export function StatusBadge({ status }: { status: TicketStatus }) {
  return <span className={`status status-${status}`}>{labels[status]}</span>;
}

