from pydantic import BaseModel, Field


class CreateInvoiceRequest(BaseModel):
    customer: str = Field(
        min_length=1,
        description="Customer name or email",
    )

    amount: int = Field(
        gt=0,
        description="Invoice amount in cents",
    )

    description: str = Field(
        min_length=1,
        description="Invoice description",
    )

    days_until_due: int = Field(
        default=7,
        gt=0,
        le=90,
        description="Number of days until the invoice is due",
    )