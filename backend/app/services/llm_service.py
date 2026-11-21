import json
import logging
from functools import lru_cache
from typing import Literal

from pydantic import BaseModel, Field

from app.config import get_settings
from app.graph.nodes.entities import extract_entities
from app.graph.nodes.intent import detect_intent
from app.graph.nodes.resolution import check_resolution
from app.graph.state import SupportState
from app.schemas.entities import ExtractedIssueData
from app.schemas.intent import IntentResult


logger = logging.getLogger(__name__)


class IssueAnalysis(BaseModel):
    intent: IntentResult
    entities: ExtractedIssueData


class ResolutionAssessment(BaseModel):
    outcome: Literal["resolved", "failed", "unclear"]
    summary: str = Field(description="A short factual summary of the customer's result.")


@lru_cache
def get_groq_model():
    settings = get_settings()
    if not settings.groq_api_key or settings.groq_api_key == "your_groq_key":
        return None

    from langchain_groq import ChatGroq

    return ChatGroq(
        api_key=settings.groq_api_key,
        model=settings.groq_model,
        temperature=0,
        timeout=settings.groq_timeout_seconds,
        max_retries=1,
    )


def analyze_issue(state: SupportState) -> dict:
    model = get_groq_model()
    if model is None:
        return _fallback_analysis(state)

    existing_context = {
        "intent": state.get("intent"),
        "entities": state.get("extracted_entities", {}),
    }
    system_prompt = """
You classify customer-support messages for a fictional e-commerce store.
Return only the requested structured output. Supported intents are:
order_not_received, payment_failed, payment_success_order_missing,
account_login_problem, password_reset, delivery_delay, human_agent_request, unknown.
Use only facts stated by the customer. Never invent an order ID, transaction ID,
email, date, error, platform, product, or payment method. Preserve useful facts from
the existing ticket context. A direct request for a person is human_agent_request.
Choose unknown when the issue is outside the supported store topics.
""".strip()
    user_prompt = (
        f"Existing ticket context:\n{json.dumps(existing_context, default=str)}\n\n"
        f"Latest customer message:\n{state.get('latest_user_message', '')}"
    )

    try:
        result = model.with_structured_output(IssueAnalysis).invoke(
            [("system", system_prompt), ("human", user_prompt)]
        )
        existing = state.get("extracted_entities", {})
        entities = {
            key: value if value is not None else existing.get(key)
            for key, value in result.entities.model_dump().items()
        }
        return {
            **result.intent.model_dump(),
            "extracted_entities": entities,
            "llm_used": True,
            "llm_model": get_settings().groq_model,
            "llm_error": None,
        }
    except Exception as exc:
        logger.warning("Groq issue analysis failed; using deterministic fallback: %s", exc)
        return _fallback_analysis(state, exc)


def assess_resolution(state: SupportState) -> dict:
    attempted = state.get("attempted_steps", [])
    if not attempted or attempted[-1].get("outcome") != "waiting":
        return {}

    model = get_groq_model()
    if model is None:
        return check_resolution(state)

    latest_step = attempted[-1]
    prompt = (
        "Decide whether the customer's latest reply says the troubleshooting step "
        "resolved the original issue, failed to resolve it, or is unclear. Do not infer "
        "success from politeness or from the word 'yes' alone.\n\n"
        f"Issue: {state.get('intent', 'unknown')}\n"
        f"Step: {latest_step.get('title')}\n"
        f"Customer reply: {state.get('latest_user_message', '')}"
    )

    try:
        result = model.with_structured_output(ResolutionAssessment).invoke(prompt)
        updated_attempts = [step.copy() for step in attempted]
        updated_attempts[-1] = updated_attempts[-1] | {
            "customer_result": result.summary,
            "outcome": result.outcome,
        }
        status = {
            "resolved": "resolved",
            "failed": "unresolved",
            "unclear": "waiting_for_customer",
        }[result.outcome]
        draft = {
            "resolved": "I am glad that worked. I will mark this ticket as resolved.",
            "failed": "",
            "unclear": "Did that step resolve the original issue?",
        }[result.outcome]
        return {
            "attempted_steps": updated_attempts,
            "resolution_status": status,
            "final_answer": draft,
            "llm_used": True,
            "llm_model": get_settings().groq_model,
            "llm_error": None,
        }
    except Exception as exc:
        logger.warning("Groq resolution assessment failed; using deterministic fallback: %s", exc)
        return check_resolution(state) | {"llm_error": _error_label(exc)}


def generate_customer_response(state: SupportState) -> dict:
    draft = state.get("final_answer", "")
    model = get_groq_model()
    if model is None or not draft:
        return {}

    documents = [
        {"title": doc.get("title"), "snippet": doc.get("snippet")}
        for doc in state.get("retrieved_documents", [])[:2]
    ]
    prompt = (
        "Rewrite the approved draft as a warm, concise customer-support response. "
        "Keep the exact action and meaning. Do not add troubleshooting steps, policies, "
        "promises, refunds, or facts. Never request passwords, OTPs, CVVs, or full card "
        "numbers. Return plain text in no more than three sentences.\n\n"
        f"Customer message: {state.get('latest_user_message', '')}\n"
        f"Approved draft: {draft}\n"
        f"Retrieved guidance: {json.dumps(documents)}"
    )

    try:
        response = model.invoke([("system", "You are QuickCart's careful support assistant."), ("human", prompt)])
        content = response.content if isinstance(response.content, str) else str(response.content)
        return {
            "final_answer": content.strip() or draft,
            "llm_used": True,
            "llm_model": get_settings().groq_model,
        }
    except Exception as exc:
        logger.warning("Groq response generation failed; keeping approved draft: %s", exc)
        return {"llm_error": _error_label(exc)}


def _fallback_analysis(state: SupportState, error: Exception | None = None) -> dict:
    result = detect_intent(state)
    working_state = state | result
    return result | extract_entities(working_state) | {
        "llm_used": False,
        "llm_model": None,
        "llm_error": _error_label(error) if error else None,
    }


def _error_label(error: Exception) -> str:
    return f"{type(error).__name__}: Groq request failed"
