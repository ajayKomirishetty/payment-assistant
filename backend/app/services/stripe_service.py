import stripe
from datetime import datetime, timezone

from app.core.config import settings

class StripeService:
    def __init__(self):
        self.client = stripe.StripeClient(
            settings.stripe_secret_key
        )

    # -------------------------
    # Customers
    # -------------------------

    def list_customers(self, limit: int = 10):
        return self.client.customers.list(
            params={"limit": limit}
        )

    def find_customer_by_email(self, email: str):
      email = email.strip().lower()

      customers = self.client.customers.list(
          params={
              "email": email,
              "limit": 1,
          }
      )

      return customers.data[0] if customers.data else None

    def find_customer(self, name_or_email: str):
        """
        Find a customer by email, exact name, or partial name.
        """

        search_term = name_or_email.strip().lower()

        # Try exact email first
        customer = self.find_customer_by_email(search_term)

        if customer:
            return customer

        # Search customers by name
        customers = self.client.customers.list(
            params={"limit": 100}
        )

        # First try exact name
        for customer in customers.data:
            if (
                customer.name
                and customer.name.lower() == search_term
            ):
                return customer

        # Then try partial name
        matches = [
            customer
            for customer in customers.data
            if customer.name
            and search_term in customer.name.lower()
        ]

        if len(matches) == 1:
            return matches[0]

        return None

    # -------------------------
    # Payments
    # -------------------------

    def get_successful_payments_between(
      self,
      start_date: datetime,
      end_date: datetime,
    ):
      """
      Return successful payments created between start_date
      and end_date.

      Stripe timestamps are Unix timestamps, so we convert
      the Python datetimes to timestamps before querying.
      """

      payments = self.client.payment_intents.list(
          params={
              "created": {
                  "gte": int(start_date.timestamp()),
                  "lt": int(end_date.timestamp()),
              },
              "limit": 100,
          }
      )

      return [
          payment
          for payment in payments.data
          if payment.status == "succeeded"
      ]

    def list_payments(self, limit: int = 20):
        return self.client.payment_intents.list(
            params={"limit": limit}
        )

    def get_payment(self, payment_id: str):
        return self.client.payment_intents.retrieve(
            payment_id
        )

    def get_latest_payment(self, customer_id: str):
        """
        Return the most recent PaymentIntent
        for a customer.
        """

        payments = self.client.payment_intents.list(
            params={
                "customer": customer_id,
                "limit": 1,
            }
        )

        return payments.data[0] if payments.data else None

    def get_refunded_amount(self, payment_id: str) -> int:
        """
        Return the total amount already refunded
        for a payment, in cents.
        """

        refunds = self.client.refunds.list(
            params={
                "payment_intent": payment_id,
                "limit": 100,
            }
        )

        return sum(
            refund.amount
            for refund in refunds.data
            if refund.status != "failed"
        )

    def get_latest_refundable_payment(self, customer_id: str):
        """
        Return the customer's most recent payment
        that still has a refundable amount.
        """

        payments = self.client.payment_intents.list(
            params={
                "customer": customer_id,
                "limit": 10,
            }
        )

        for payment in payments.data:
            if payment.status != "succeeded":
                continue

            refunded_amount = self.get_refunded_amount(
                payment.id
            )

            if refunded_amount < payment.amount:
                return payment

        return None

    def create_payment(
        self,
        customer_id: str,
        amount: int,
        description: str,
    ):
        """
        Create and confirm a test payment.

        Amount is in cents.
        Example: $120.00 = 12000.
        """

        return self.client.payment_intents.create(
            params={
                "amount": amount,
                "currency": "usd",
                "customer": customer_id,
                "payment_method": "pm_card_visa",
                "confirm": True,
                "description": description,
                "automatic_payment_methods": {
                    "enabled": True,
                    "allow_redirects": "never",
                },
            }
        )

    # -------------------------
    # Refunds
    # -------------------------

    def refund_payment(
        self,
        payment_id: str,
        amount: int | None = None,
    ):
        """
        Refund a succeeded payment.

        Amount is optional and expressed in cents.
        If omitted, the remaining refundable amount
        is refunded.
        """

        payment = self.get_payment(payment_id)

        if payment.status != "succeeded":
            raise ValueError(
                f"Payment {payment_id} cannot be refunded "
                f"because its status is '{payment.status}'."
            )

        refunded_amount = self.get_refunded_amount(
            payment_id
        )

        refundable_amount = payment.amount - refunded_amount

        if refundable_amount <= 0:
            raise ValueError(
                f"Payment {payment_id} has already been "
                "fully refunded."
            )

        params = {
            "payment_intent": payment_id,
        }

        if amount is not None:
            if amount <= 0:
                raise ValueError(
                    "Refund amount must be greater than zero."
                )

            if amount > refundable_amount:
                raise ValueError(
                    "Refund amount cannot exceed the "
                    "remaining refundable amount."
                )

            params["amount"] = amount

        return self.client.refunds.create(
            params=params
        )

    # -------------------------
    # Invoices
    # -------------------------

    def list_invoices(self, limit: int = 20):
        return self.client.invoices.list(
            params={"limit": limit}
        )

    def get_invoice(self, invoice_id: str):
        return self.client.invoices.retrieve(
            invoice_id
        )

    def create_invoice(
      self,
      customer_id: str,
      amount: int,
      description: str,
      days_until_due: int = 7,
    ):
      """
      Create an invoice with a single line item.

      Amount is expressed in the smallest currency unit.
      For example:
        USD 250.00 = 25000 cents
        CAD 250.00 = 25000 cents
      """

      invoice = self.client.invoices.create(
          params={
              "customer": customer_id,
              "collection_method": "send_invoice",
              "days_until_due": days_until_due,
              "auto_advance": False,
          }
      )

      # Stripe determines the invoice currency based on
      # the customer/invoice configuration.
      currency = invoice.currency

      self.client.invoice_items.create(
          params={
              "customer": customer_id,
              "amount": amount,
              "currency": currency,
              "description": description,
              "invoice": invoice.id,
          }
      )

      invoice = self.client.invoices.finalize_invoice(
          invoice.id
      )

      return invoice

    # -------------------------
    # Payment Links
    # -------------------------

    def get_today_payment_summary(self):
      now = datetime.now(timezone.utc)

      start_of_day = now.replace(
          hour=0,
          minute=0,
          second=0,
          microsecond=0,
      )

      payments = self.client.payment_intents.list(
          params={
              "created": {
                  "gte": int(start_of_day.timestamp()),
                  "lte": int(now.timestamp()),
              },
              "limit": 100,
          }
      )

      successful_payments = []
      failed_payments = []

      for payment in payments.data:
          if payment.status == "succeeded":
              successful_payments.append(payment)

          elif payment.status in {
              "failed",
              "canceled",
          }:
              failed_payments.append(payment)

      total_revenue = sum(
          payment.amount
          for payment in successful_payments
      )

      largest_payment = max(
          successful_payments,
          key=lambda payment: payment.amount,
          default=None,
      )

      return {
          "successful_payment_count": len(
              successful_payments
          ),
          "failed_payment_count": len(
              failed_payments
          ),
          "total_revenue": total_revenue,
          "largest_payment": (
              {
                  "amount": largest_payment.amount,
                  "customer": largest_payment.customer,
                  "payment_id": largest_payment.id,
              }
              if largest_payment
              else None
          ),
      }
    
    def get_open_customer_invoices(
      self,
      customer_id: str,
    ):
      invoices = self.client.invoices.list(
          params={
              "customer": customer_id,
              "status": "open",
              "limit": 10,
          }
      )

      return invoices.data