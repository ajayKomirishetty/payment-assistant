from datetime import date, datetime, timedelta, timezone

from app.schemas.assistant import PaymentCommand
from app.services.llm_service import LLMService
from app.services.stripe_service import StripeService


class AssistantService:
    def __init__(self):
        self.stripe_service = StripeService()
        self.llm_service = LLMService()

    def process(self, message: str):
        command = self.llm_service.parse_command(message)

        if command.intent == "refund_payment":
            return self.refund_payment(command)

        if command.intent == "create_invoice":
            return self.create_invoice(command)

        if command.intent == "payment_comparison":
            return self.compare_payments()

        if command.intent == "daily_summary":
            return self.daily_summary()

        raise ValueError(
            "I don't know how to handle that request."
        )

    # -------------------------
    # Refund
    # -------------------------

    def refund_payment(self, command: PaymentCommand):
        if not command.customer_name:
            raise ValueError(
                "A customer is required for a refund."
            )

        customer = self.stripe_service.find_customer(
            command.customer_name
        )

        if not customer:
            raise ValueError(
                f"Customer '{command.customer_name}' "
                "was not found."
            )

        payment = (
            self.stripe_service
            .get_latest_refundable_payment(customer.id)
        )

        if not payment:
            raise ValueError(
                f"No refundable payments found for "
                f"{customer.name}."
            )

        refund = self.stripe_service.refund_payment(
            payment.id
        )

        return {
            "message": (
                f"Refunded ${refund.amount / 100:.2f} "
                f"payment for {customer.name}."
            ),
            "success": True,
            "intent": command.intent,
            "customer": customer.name,
            "payment_id": payment.id,
            "refund_id": refund.id,
            "amount": refund.amount,
        }

    # -------------------------
    # Payment comparison
    # -------------------------

    def compare_payments(self):
        today = date.today()

        # Monday of the current week
        current_week_start = today - timedelta(
            days=today.weekday()
        )

        # Monday of the previous week
        previous_week_start = current_week_start - timedelta(
            days=7
        )

        current_week_start_datetime = datetime.combine(
            current_week_start,
            datetime.min.time(),
            tzinfo=timezone.utc,
        )

        previous_week_start_datetime = datetime.combine(
            previous_week_start,
            datetime.min.time(),
            tzinfo=timezone.utc,
        )

        payments = self.stripe_service.list_payments(
            limit=100
        )

        current_week_total = 0
        previous_week_total = 0

        for payment in payments.data:
            if payment.status != "succeeded":
                continue

            payment_date = datetime.fromtimestamp(
                payment.created,
                tz=timezone.utc,
            )

            # Previous week
            if (
                previous_week_start_datetime
                <= payment_date
                < current_week_start_datetime
            ):
                previous_week_total += payment.amount

            # Current week
            elif payment_date >= current_week_start_datetime:
                current_week_total += payment.amount

        current_week_dollars = current_week_total / 100
        previous_week_dollars = previous_week_total / 100

        if previous_week_total > 0:
            change = (
                (current_week_total - previous_week_total)
                / previous_week_total
            ) * 100

            if change > 0:
                comparison = (
                    f"an increase of {abs(change):.1f}%"
                )
            elif change < 0:
                comparison = (
                    f"a decrease of {abs(change):.1f}%"
                )
            else:
                comparison = "no change"
        else:
            comparison = (
                "no previous-week revenue to compare against"
            )

        return {
            "message": (
                f"We took ${current_week_dollars:,.2f} this week "
                f"compared with ${previous_week_dollars:,.2f} "
                f"last week — {comparison}."
            ),
            "success": True,
            "intent": "payment_comparison",
            "current_week": {
                "start": current_week_start.isoformat(),
                "end": today.isoformat(),
                "total": current_week_total,
            },
            "previous_week": {
                "start": previous_week_start.isoformat(),
                "end": (
                    current_week_start - timedelta(days=1)
                ).isoformat(),
                "total": previous_week_total,
            },
        }

    # -------------------------
    # Create invoice
    # -------------------------

    def create_invoice(self, command: PaymentCommand):
        if not command.customer_name:
            raise ValueError(
                "A customer is required for an invoice."
            )

        if command.amount is None:
            raise ValueError(
                "An invoice amount is required."
            )

        customer = self.stripe_service.find_customer(
            command.customer_name
        )

        if not customer:
            raise ValueError(
                f"Customer '{command.customer_name}' "
                "was not found."
            )

        amount_cents = int(command.amount * 100)

        if command.due_date:
            days_until_due = (
                command.due_date - date.today()
            ).days

            if days_until_due <= 0:
                raise ValueError(
                    "The invoice due date must be in the future."
                )
        else:
            days_until_due = 7

        invoice = self.stripe_service.create_invoice(
            customer_id=customer.id,
            amount=amount_cents,
            description="Invoice created by AI assistant",
            days_until_due=days_until_due,
        )

        return {
            "message": (
                f"Created a ${command.amount:.2f} invoice "
                f"for {customer.name}."
            ),
            "success": True,
            "intent": command.intent,
            "customer": customer.name,
            "invoice_id": invoice.id,
            "amount": amount_cents,
            "status": invoice.status,
            "due_date": command.due_date,
        }

    def daily_summary(self):
      payment_summary = (
          self.stripe_service
          .get_today_payment_summary()
      )

      summary = (
          self.llm_service
          .generate_daily_summary(payment_summary)
      )

      return {
          "message": summary,
          "success": True,
          "intent": "daily_summary",
          "data": payment_summary,
      }