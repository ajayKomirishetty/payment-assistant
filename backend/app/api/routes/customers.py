from fastapi import APIRouter, HTTPException

from app.services.stripe_service import StripeService


router = APIRouter(
    prefix="/api/customers",
    tags=["customers"],
)


@router.get("")
def list_customers():
    stripe_service = StripeService()

    customers = stripe_service.list_customers()

    return [
        {
            "id": customer.id,
            "name": customer.name,
            "email": customer.email,
        }
        for customer in customers.data
    ]


@router.get("/{name_or_email}")
def get_customer(name_or_email: str):
    stripe_service = StripeService()

    customer = stripe_service.find_customer(name_or_email)

    if not customer:
        raise HTTPException(
            status_code=404,
            detail="Customer not found",
        )

    return {
        "id": customer.id,
        "name": customer.name,
        "email": customer.email,
    }


@router.get("/{name_or_email}/latest-payment")
def get_latest_payment(name_or_email: str):
    stripe_service = StripeService()

    customer = stripe_service.find_customer(name_or_email)

    if not customer:
        raise HTTPException(
            status_code=404,
            detail="Customer not found",
        )

    payment = stripe_service.get_latest_payment(customer.id)

    if not payment:
        raise HTTPException(
            status_code=404,
            detail="No payments found",
        )

    return {
        "id": payment.id,
        "amount": payment.amount,
        "currency": payment.currency,
        "status": payment.status,
        "description": payment.description,
    }