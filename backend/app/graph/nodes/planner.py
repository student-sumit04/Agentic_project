from app.graph.state import SupportState


PLANS = {
    "payment_success_order_missing": [
        {
            "id": "pay-account-match",
            "title": "Confirm account identity",
            "instruction": "Please check whether you are signed in with the same email or phone number used during payment.",
            "expected_signal": "Customer confirms they are using the same account or found the order in another account.",
        },
        {
            "id": "pay-transaction-age",
            "title": "Check transaction age",
            "instruction": "Please confirm whether the successful payment happened more than 30 minutes ago.",
            "expected_signal": "Customer confirms whether reconciliation time has already passed.",
        },
    ],
    "payment_failed": [
        {
            "id": "pay-bank-status",
            "title": "Confirm debit status",
            "instruction": "Please check whether the amount was actually deducted from your bank or wallet statement.",
            "expected_signal": "Customer confirms deducted or not deducted.",
        }
    ],
    "account_login_problem": [
        {
            "id": "acc-reset",
            "title": "Try password reset",
            "instruction": "Please use the password reset option for your registered email and tell me whether the reset email arrives.",
            "expected_signal": "Customer receives the reset email or reports that it did not arrive.",
        }
    ],
    "delivery_delay": [
        {
            "id": "del-tracking",
            "title": "Check tracking status",
            "instruction": "Please open the order tracking page and tell me whether it shows delayed, out for delivery, or delivery attempted.",
            "expected_signal": "Customer provides the current tracking status.",
        }
    ],
}


def create_troubleshooting_plan(state: SupportState) -> dict:
    plan = PLANS.get(state.get("intent"), [])
    if not plan:
        return {
            "resolution_status": "escalated",
            "escalation_reason": "Unsupported issue for the MVP workflow",
        }
    return {
        "troubleshooting_plan": plan,
        "current_step_index": state.get("current_step_index", 0),
    }


def present_next_step(state: SupportState) -> dict:
    plan = state.get("troubleshooting_plan", [])
    attempted = state.get("attempted_steps", [])
    index = len(attempted)

    if index >= len(plan):
        return {
            "resolution_status": "escalated",
            "escalation_reason": "Troubleshooting steps exhausted",
        }

    step = plan[index]
    return {
        "current_step_index": index,
        "attempted_steps": attempted + [{"step_id": step["id"], "title": step["title"], "outcome": "waiting"}],
        "resolution_status": "waiting_for_customer",
        "final_answer": step["instruction"],
    }

