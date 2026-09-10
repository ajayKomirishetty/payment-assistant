from fastapi import APIRouter

import stripe

from app.core.config import settings


router = APIRouter(
    prefix="/api/invoices",
    tags=["invoices"],
)


stripe.api_key = settings.stripe_secret_key


@router.get("")
def list_invoices():
    invoices = stripe.Invoice.list(limit=20)

    return [
        {
            "id": invoice.id,
            "customer": invoice.customer,
            "amount_due": invoice.amount_due,
            "currency": invoice.currency,
            "status": invoice.status,
        }
        for invoice in invoices.data
    ]