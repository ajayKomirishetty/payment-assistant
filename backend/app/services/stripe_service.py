import stripe

from app.core.config import settings


class StripeService:
    def __init__(self):
        stripe.api_key = settings.stripe_secret_key

    def list_customers(self, limit: int = 10):
        return stripe.Customer.list(limit=limit)

    def list_payments(self, limit: int = 10):
        return stripe.PaymentIntent.list(limit=limit)