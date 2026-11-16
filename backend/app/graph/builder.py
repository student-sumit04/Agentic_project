from functools import lru_cache
from typing import Literal

from langgraph.graph import END, START, StateGraph

from app.graph.nodes.escalation import escalate_case
from app.graph.nodes.planner import create_troubleshooting_plan, present_next_step
from app.graph.nodes.safety import detect_safety_and_urgency
from app.graph.nodes.validation import ask_for_information, check_missing_information
from app.graph.state import SupportState
from app.rag.retriever import retrieve_knowledge
from app.services.llm_service import analyze_issue, assess_resolution, generate_customer_response


def _after_safety(state: SupportState) -> Literal["escalate", "resolution_check"]:
    return "escalate" if state.get("requires_immediate_escalation") else "resolution_check"


def _after_resolution(
    state: SupportState,
) -> Literal["analyze_issue", "present_step", "respond"]:
    attempted = state.get("attempted_steps", [])
    if not attempted:
        return "analyze_issue"

    outcome = attempted[-1].get("outcome")
    if outcome == "failed":
        return "present_step"
    if outcome in {"resolved", "unclear"}:
        return "respond"
    return "analyze_issue"


def _after_analysis(state: SupportState) -> Literal["escalate", "validate"]:
    return "escalate" if state.get("intent") == "human_agent_request" else "validate"


def _after_validation(state: SupportState) -> Literal["ask", "retrieve"]:
    return "ask" if state.get("missing_fields") else "retrieve"


def _after_plan(state: SupportState) -> Literal["escalate", "present_step"]:
    return "escalate" if state.get("resolution_status") == "escalated" else "present_step"


def _after_present(state: SupportState) -> Literal["escalate", "respond"]:
    return "escalate" if state.get("resolution_status") == "escalated" else "respond"


@lru_cache
def build_support_graph():
    builder = StateGraph(SupportState)
    builder.add_node("safety", detect_safety_and_urgency)
    builder.add_node("resolution_check", assess_resolution)
    builder.add_node("analyze_issue", analyze_issue)
    builder.add_node("validate", check_missing_information)
    builder.add_node("ask", ask_for_information)
    builder.add_node("retrieve", retrieve_knowledge)
    builder.add_node("plan", create_troubleshooting_plan)
    builder.add_node("present_step", present_next_step)
    builder.add_node("escalate", escalate_case)
    builder.add_node("respond", generate_customer_response)

    builder.add_edge(START, "safety")
    builder.add_conditional_edges("safety", _after_safety)
    builder.add_conditional_edges("resolution_check", _after_resolution)
    builder.add_conditional_edges("analyze_issue", _after_analysis)
    builder.add_conditional_edges("validate", _after_validation)
    builder.add_edge("ask", "respond")
    builder.add_edge("retrieve", "plan")
    builder.add_conditional_edges("plan", _after_plan)
    builder.add_conditional_edges("present_step", _after_present)
    builder.add_edge("escalate", "respond")
    builder.add_edge("respond", END)
    return builder.compile()


support_graph = build_support_graph()


def run_support_workflow(state: SupportState) -> SupportState:
    initial_state = state | {
        "orchestration_engine": "langgraph",
        "llm_used": False,
        "llm_model": None,
        "llm_error": None,
    }
    return support_graph.invoke(
        initial_state,
        config={"configurable": {"thread_id": state.get("ticket_id", "untracked")}},
    )
