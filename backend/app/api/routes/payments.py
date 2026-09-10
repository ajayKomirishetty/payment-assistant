from fastapi import APIRouter

from app.services.stripe_service import StripeService


router = APIRouter(
    prefix="/api/payments",
    tags=["payments"],
)


@router.get("")
def list_payments():
    stripe_service = StripeService()

    payments = stripe_service.list_payments()

    return [
        {
            "id": payment.id,
            "amount": payment.amount,
            "currency": payment.currency,
            "status": payment.status,
            "customer": payment.customer,
            "description": payment.description,
        }
        for payment in payments.data
    ]