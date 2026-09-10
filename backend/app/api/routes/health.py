from fastapi import APIRouter

from app.services.stripe_service import StripeService


router = APIRouter(
    prefix="/api",
    tags=["health"],
)


@router.get("/health")
def health_check():
    return {
        "status": "ok"
    }


@router.get("/stripe-test")
def stripe_test():
    stripe_service = StripeService()

    customers = stripe_service.list_customers()

    return {
        "customer_count": len(customers.data),
        "customers": [
            {
                "id": customer.id,
                "name": customer.name,
                "email": customer.email,
            }
            for customer in customers.data
        ],
    }