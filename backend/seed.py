import stripe

from app.core.config import settings


stripe.api_key = settings.stripe_secret_key


def get_or_create_customer(
    name: str,
    email: str,
) -> stripe.Customer:
    """
    Find a customer by email or create them if they don't exist.

    This makes the seed safe to run more than once for customers.
    """
    existing = stripe.Customer.list(
        email=email,
        limit=1,
    )

    if existing.data:
        customer = existing.data[0]
        print(f"Customer already exists: {customer.name} ({customer.id})")
        return customer

    customer = stripe.Customer.create(
        name=name,
        email=email,
    )

    print(f"Created customer: {customer.name} ({customer.id})")
    return customer


def create_successful_payment(
    customer: stripe.Customer,
    amount: int,
    description: str,
) -> stripe.PaymentIntent:
    """
    Create a successful Stripe test payment using Stripe's test Visa card.
    """
    payment = stripe.PaymentIntent.create(
        amount=amount,
        currency="usd",
        customer=customer.id,
        payment_method="pm_card_visa",
        confirm=True,
        description=description,
        automatic_payment_methods={
            "enabled": True,
            "allow_redirects": "never",
        },
    )

    print(
        f"Created payment: {payment.id} "
        f"${amount / 100:.2f} for {customer.name}"
    )

    return payment


def create_declined_payment(
    customer: stripe.Customer,
    amount: int,
    description: str,
) -> stripe.PaymentIntent:
    """
    Create a declined test payment.

    Stripe's pm_card_chargeDeclined test payment method produces
    a failed payment attempt without moving real money.
    """
    try:
        payment = stripe.PaymentIntent.create(
            amount=amount,
            currency="usd",
            customer=customer.id,
            payment_method="pm_card_chargeDeclined",
            confirm=True,
            description=description,
            automatic_payment_methods={
                "enabled": True,
                "allow_redirects": "never",
            },
        )

        print(
            f"Created declined payment: {payment.id} "
            f"for {customer.name}"
        )

        return payment

    except stripe.error.CardError as exc:
        # Stripe can raise CardError immediately for a declined
        # confirmation. This is expected for this seed operation.
        payment_intent = getattr(exc, "payment_intent", None)

        if payment_intent:
            print(
                f"Created declined payment: {payment_intent.id} "
                f"for {customer.name}"
            )
            return payment_intent

        print(
            f"Declined payment simulated for {customer.name}: "
            f"{exc.user_message or str(exc)}"
        )

        return None


def create_invoice(
    customer: stripe.Customer,
    amount: int,
    description: str,
    days_until_due: int = 7,
) -> stripe.Invoice:
    """
    Create an open, send_invoice invoice.

    The invoice is finalized but intentionally left unpaid so that
    the Telegram customer bot can display and pay it.
    """
    invoice = stripe.Invoice.create(
        customer=customer.id,
        collection_method="send_invoice",
        days_until_due=days_until_due,
        auto_advance=False,
    )

    stripe.InvoiceItem.create(
        customer=customer.id,
        amount=amount,
        currency="usd",
        description=description,
        invoice=invoice.id,
    )

    invoice = stripe.Invoice.finalize_invoice(invoice.id)

    print(
        f"Created invoice: {invoice.id} "
        f"${amount / 100:.2f} for {customer.name}"
    )

    return invoice


def main():
    print("Starting Stripe test data seed...\n")

    # ------------------------------------------------------------------
    # Customers
    # ------------------------------------------------------------------

    customers = {
        "maya": get_or_create_customer(
            name="Maya Johnson",
            email="maya@example.com",
        ),
        "acme": get_or_create_customer(
            name="Acme Corp",
            email="billing@acme.example.com",
        ),
        "john": get_or_create_customer(
            name="John Smith",
            email="john@example.com",
        ),
        "sarah": get_or_create_customer(
            name="Sarah Williams",
            email="sarah@example.com",
        ),
    }

    print("\nCustomers ready.\n")

    # ------------------------------------------------------------------
    # Successful payments
    # ------------------------------------------------------------------

    create_successful_payment(
        customer=customers["maya"],
        amount=12000,
        description="Maya payment",
    )

    create_successful_payment(
        customer=customers["maya"],
        amount=8000,
        description="Maya second payment",
    )

    create_successful_payment(
        customer=customers["acme"],
        amount=50000,
        description="Acme Corp payment",
    )

    create_successful_payment(
        customer=customers["john"],
        amount=35000,
        description="John Smith payment",
    )

    # ------------------------------------------------------------------
    # Declined payment
    # ------------------------------------------------------------------

    create_declined_payment(
        customer=customers["sarah"],
        amount=7500,
        description="Sarah declined payment",
    )

    # ------------------------------------------------------------------
    # Open invoice
    # ------------------------------------------------------------------

    create_invoice(
        customer=customers["acme"],
        amount=120000,
        description="Acme Corp outstanding invoice",
        days_until_due=7,
    )

    print("\nSeed completed successfully.")
    print("\nTest customers:")
    print("  Maya Johnson       maya@example.com")
    print("  Acme Corp          billing@acme.example.com")
    print("  John Smith         john@example.com")
    print("  Sarah Williams     sarah@example.com")

    print("\nSeeded payments:")
    print("  Maya       $120.00")
    print("  Maya       $80.00")
    print("  Acme       $500.00")
    print("  John       $350.00")
    print("  Sarah      $75.00 declined")

    print("\nSeeded invoice:")
    print("  Acme       $1,200.00 open")


if __name__ == "__main__":
    main()