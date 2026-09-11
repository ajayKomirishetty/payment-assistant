from unittest.mock import Mock, patch

from app.schemas.assistant import PaymentCommand
from app.services.assistant_service import AssistantService


def test_refund_requires_customer():
    service = AssistantService()

    command = PaymentCommand(
        intent="refund_payment",
    )

    try:
        service.refund_payment(command)
        assert False, "Expected ValueError"
    except ValueError as exc:
        assert str(exc) == "A customer is required for a refund."


@patch("app.services.assistant_service.StripeService")
def test_refund_unknown_customer(mock_stripe):
    service = AssistantService()

    service.stripe_service.find_customer.return_value = None

    command = PaymentCommand(
        intent="refund_payment",
        customer_name="Unknown Customer",
    )

    try:
        service.refund_payment(command)
        assert False, "Expected ValueError"
    except ValueError as exc:
        assert "Unknown Customer" in str(exc)


@patch("app.services.assistant_service.StripeService")
def test_create_invoice_requires_amount(mock_stripe):
    service = AssistantService()

    command = PaymentCommand(
        intent="create_invoice",
        customer_name="Maya Johnson",
    )

    try:
        service.create_invoice(command)
        assert False, "Expected ValueError"
    except ValueError as exc:
        assert str(exc) == "An invoice amount is required."