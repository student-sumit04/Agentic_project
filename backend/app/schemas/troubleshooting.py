from typing import Literal

from pydantic import BaseModel


class TroubleshootingStep(BaseModel):
    id: str
    title: str
    instruction: str
    expected_signal: str


class AttemptedStep(BaseModel):
    step_id: str
    title: str
    customer_result: str | None = None
    outcome: Literal["waiting", "resolved", "failed", "unclear"] = "waiting"

