from pydantic import BaseModel


class ExtractedIssueData(BaseModel):
    order_id: str | None = None
    transaction_id: str | None = None
    product_name: str | None = None
    account_email: str | None = None
    issue_start_date: str | None = None
    error_message: str | None = None
    platform: str | None = None
    payment_method: str | None = None

