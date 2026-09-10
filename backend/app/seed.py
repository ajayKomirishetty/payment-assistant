import stripe

from app.core.config import settings


stripe.api_key = settings.stripe_secret_key


CUSTOMERS = [
    {
        "name": "Maya Johnson",
        "email": "maya@example.com",
    },
    {
        "name": "Acme Corp",
        "email": "billing@acme.example.com",
    },
    {
        "name": "John Smith",
        "email": "john@example.com",
    },
    {
        "name": "Sarah Williams",
        "email": "sarah@example.com",
    },
]


def find_customer_by_email(email: str):
    customers = stripe.Customer.list(
        email=email,
        limit=1,
    )

    return customers.data[0] if customers.data else None


def create_customer(customer_data: dict):
    existing_customer = find_customer_by_email(
        customer_data["email"]
    )

    if existing_customer:
        print(
            f"Customer already exists: "
            f"{existing_customer.name} "
            f"({existing_customer.id})"
        )
        return existing_customer

    customer = stripe.Customer.create(
        name=customer_data["name"],
        email=customer_data["email"],
    )

    print(
        f"Created customer: "
        f"{customer.name} ({customer.id})"
    )

    return customer

def create_payment(customer,amount: int,description: str,):
    payment_intent = stripe.PaymentIntent.create(
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
        f"Created payment: "
        f"${amount / 100:.2f} "
        f"for {customer.name} "
        f"({payment_intent.status})"
    )

    return payment_intent


def create_customers():
    customers = {}

    for customer_data in CUSTOMERS:
        customer = create_customer(customer_data)
        customers[customer_data["email"]] = customer

    return customers


if __name__ == "__main__":
    customers = create_customers()
    create_payment(customers["maya@example.com"],12000,"Maya payment")