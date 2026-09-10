from datetime import date
from typing import Literal

from pydantic import BaseModel, Field


class AssistantRequest(BaseModel):
    message: str = Field(
        min_length=1,
        description="Natural language command from the user",
    )


class PaymentCommand(BaseModel):
    intent: Literal[
        "refund_payment",
        "create_invoice",
        "payment_comparison",
        "daily_summary",
    ]

    customer_name: str | None = None

    amount: float | None = Field(
        default=None,
        gt=0,
        description="Amount in dollars, not cents",
    )

    due_date: date | None = None

    payment_reference: str | None = None