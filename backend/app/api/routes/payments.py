from fastapi import APIRouter, HTTPException
from app.services.stripe_service import StripeService
import stripe


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


@router.post("/{payment_id}/refund")
def refund_payment(payment_id: str):
    stripe_service = StripeService()

    try:
        refund = stripe_service.refund_payment(payment_id)

        return {
            "id": refund.id,
            "payment_intent": refund.payment_intent,
            "amount": refund.amount,
            "currency": refund.currency,
            "status": refund.status,
        }

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    except stripe.StripeError as exc:
        raise HTTPException(
            status_code=400,
            detail="Stripe could not process the refund.",
        )
    stripe_service = StripeService()

    try:
        refund = stripe_service.refund_payment(payment_id)

        return {
            "id": refund.id,
            "payment_intent": refund.payment_intent,
            "amount": refund.amount,
            "currency": refund.currency,
            "status": refund.status,
        }

    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )