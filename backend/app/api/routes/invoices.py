from fastapi import APIRouter, HTTPException

from app.schemas.invoice import CreateInvoiceRequest
from app.services.stripe_service import StripeService


router = APIRouter(
    prefix="/api/invoices",
    tags=["invoices"],
)


@router.get("")
def list_invoices():
    stripe_service = StripeService()

    invoices = stripe_service.list_invoices()

    return [
        {
            "id": invoice.id,
            "customer": invoice.customer,
            "amount_due": invoice.amount_due,
            "currency": invoice.currency,
            "status": invoice.status,
            "due_date": invoice.due_date,
        }
        for invoice in invoices.data
    ]


@router.post("")
def create_invoice(request: CreateInvoiceRequest):
    stripe_service = StripeService()

    customer = stripe_service.find_customer(
        request.customer
    )

    if not customer:
        raise HTTPException(
            status_code=404,
            detail=f"Customer '{request.customer}' not found.",
        )

    try:
        invoice = stripe_service.create_invoice(
            customer_id=customer.id,
            amount=request.amount,
            description=request.description,
            days_until_due=request.days_until_due,
        )

        return {
            "id": invoice.id,
            "customer": customer.id,
            "customer_name": customer.name,
            "amount_due": invoice.amount_due,
            "currency": invoice.currency,
            "status": invoice.status,
            "description": request.description,
            "due_date": invoice.due_date,
        }

    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )