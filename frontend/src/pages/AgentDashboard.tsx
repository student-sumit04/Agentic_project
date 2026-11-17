import { useEffect, useState } from "react";
import { listEscalations } from "../services/api";
import type { TicketSummary } from "../types/support";

export function AgentDashboard() {
  const [items, setItems] = useState<Array<{ ticket: TicketSummary; summary: string | null }>>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(false);

  useEffect(() => {
    listEscalations()
      .then(setItems)
      .catch(() => setError(true))
      .finally(() => setIsLoading(false));
  }, []);

  return (
    <section className="page-band">
      <h1>Agent Dashboard</h1>
      <div className="grid-list">
        {items.map((item) => (
          <article className="ticket-card" key={item.ticket.ticket_id}>
            <div>
              <strong>{item.ticket.ticket_id}</strong>
              <span>{item.ticket.priority}</span>
            </div>
            <pre>{item.summary}</pre>
          </article>
        ))}
        {isLoading && <p className="muted">Loading escalations...</p>}
        {error && <p className="form-error">Could not load escalations. Check that the API is running.</p>}
        {!isLoading && !error && !items.length && <p className="muted">No escalated tickets.</p>}
      </div>
    </section>
  );
}
