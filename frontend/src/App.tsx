import { NavLink, Route, Routes } from "react-router-dom";
import { BookOpen, Inbox, LayoutDashboard, MessagesSquare } from "lucide-react";
import { AgentDashboard } from "./pages/AgentDashboard";
import { ChatPage } from "./pages/ChatPage";
import { KnowledgePage } from "./pages/KnowledgePage";
import { TicketsPage } from "./pages/TicketsPage";

export function App() {
  return (
    <div className="app-shell">
      <nav className="sidebar">
        <div className="brand">QA</div>
        <NavLink to="/" title="Chat">
          <MessagesSquare size={20} />
          <span>Chat</span>
        </NavLink>
        <NavLink to="/tickets" title="Tickets">
          <Inbox size={20} />
          <span>Tickets</span>
        </NavLink>
        <NavLink to="/agents" title="Agent dashboard">
          <LayoutDashboard size={20} />
          <span>Agents</span>
        </NavLink>
        <NavLink to="/knowledge" title="Knowledge base">
          <BookOpen size={20} />
          <span>Knowledge</span>
        </NavLink>
      </nav>

      <main>
        <Routes>
          <Route path="/" element={<ChatPage />} />
          <Route path="/tickets" element={<TicketsPage />} />
          <Route path="/agents" element={<AgentDashboard />} />
          <Route path="/knowledge" element={<KnowledgePage />} />
        </Routes>
      </main>
    </div>
  );
}

