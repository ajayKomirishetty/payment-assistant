from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from app.core.config import settings
from app.services.stripe_service import StripeService


class TelegramService:
    def __init__(self):
        if not settings.telegram_bot_token:
            raise ValueError(
                "TELEGRAM_BOT_TOKEN is not configured."
            )

        self.stripe_service = StripeService()

        # Temporary authentication mapping.
        # PostgreSQL can replace this later.
        # chat_id -> Stripe customer ID
        self.customer_sessions = {}

        self.application = (
            Application.builder()
            .token(settings.telegram_bot_token)
            .build()
        )

        self.application.add_handler(
            CommandHandler("start", self.start)
        )

        self.application.add_handler(
            CommandHandler("logout", self.logout)
        )

        self.application.add_handler(
            MessageHandler(
                filters.TEXT & ~filters.COMMAND,
                self.handle_message,
            )
        )

    # --------------------------------
    # Commands
    # --------------------------------

    async def start(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
    ):
        await update.message.reply_text(
            "Welcome to the Replicant Payments Assistant.\n\n"
            "Please send your customer email to get started."
        )

    async def logout(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
    ):
        chat_id = update.effective_chat.id

        self.customer_sessions.pop(chat_id, None)

        await update.message.reply_text(
            "You have been logged out. "
            "Send your customer email to log in again."
        )

    # --------------------------------
    # Message routing
    # --------------------------------

    async def handle_message(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
    ):
        if not update.message:
            return

        message = update.message.text.strip()
        message_lower = message.lower()
        chat_id = update.effective_chat.id

        # --------------------------------
        # Authentication
        # --------------------------------

        if chat_id not in self.customer_sessions:
            customer = self.stripe_service.find_customer_by_email(
                message
            )

            if not customer:
                await update.message.reply_text(
                    "I couldn't find a customer with that email. "
                    "Please check the email and try again."
                )
                return

            self.customer_sessions[chat_id] = customer.id

            await update.message.reply_text(
                f"You're logged in as {customer.name}.\n\n"
                "You can ask about your payments and invoices."
            )

            return

        # --------------------------------
        # Authenticated customer
        # --------------------------------

        customer_id = self.customer_sessions[chat_id]

        customer = self.stripe_service.client.customers.retrieve(
            customer_id
        )

        # --------------------------------
        # Security
        #
        # Customers can only access their
        # own payments and invoices.
        # --------------------------------

        restricted_terms = [
            "revenue",
            "total revenue",
            "business revenue",
            "company revenue",
            "all customers",
            "other customers",
            "total payments",
            "how much did we make",
            "how much did the business make",
            "company finances",
            "account finances",
        ]

        if any(
            term in message_lower
            for term in restricted_terms
        ):
            await update.message.reply_text(
                "I can only provide information about "
                "your own payments and invoices."
            )
            return

        # --------------------------------
        # Pay invoice
        #
        # IMPORTANT:
        # Do NOT use:
        #
        #     if "pay" in message_lower
        #
        # because "payment" contains "pay".
        #
        # This caused:
        #
        # "What is my latest payment?"
        #
        # to be treated as an invoice payment request.
        # --------------------------------

        if self.is_invoice_payment_request(message):
            await self.handle_invoice_payment(
                update,
                customer_id,
                message,
            )
            return

        # --------------------------------
        # Payment confirmation
        # --------------------------------

        if self.is_payment_confirmation(message):
            await self.handle_payment_confirmation(
                update,
                customer_id,
            )
            return

        # --------------------------------
        # Payments
        # --------------------------------

        if "payment" in message_lower:
            await self.handle_latest_payment(
                update,
                customer_id,
            )
            return

        # --------------------------------
        # Invoices
        # --------------------------------

        if "invoice" in message_lower:
            await self.handle_invoices(
                update,
                customer_id,
            )
            return

        # --------------------------------
        # Receipts
        # --------------------------------

        if (
            "receipt" in message_lower
            or "receipts" in message_lower
        ):
            await self.handle_receipts(
                update,
                customer_id,
            )
            return

        # --------------------------------
        # Unknown request
        # --------------------------------

        await update.message.reply_text(
            "I can help with your payments and invoices.\n\n"
            "Try:\n"
            "• What is my latest payment?\n"
            "• Show my invoices\n"
            "• Pay my invoice\n"
            "• Show my receipts"
        )

    # --------------------------------
    # Request classification
    # --------------------------------

    def is_invoice_payment_request(
        self,
        message: str,
    ) -> bool:
        """
        Determine whether the customer is asking
        to pay an invoice.

        Avoid using:
            "pay" in message

        because "payment" contains "pay".
        """

        message_lower = message.lower().strip()

        return (
            message_lower == "pay"
            or "pay my invoice" in message_lower
            or "pay this invoice" in message_lower
            or "pay this" in message_lower
            or message_lower.startswith("pay invoice")
            or message_lower.startswith("pay the invoice")
        )

    def is_payment_confirmation(
        self,
        message: str,
    ) -> bool:
        """
        Detect simple messages indicating that the
        customer believes they completed payment.

        The actual payment state is always determined
        from Stripe, not from the customer's message.
        """

        message_lower = message.lower().strip()

        return message_lower in {
            "paid",
            "i paid",
            "done",
            "done paying",
            "payment done",
            "payment completed",
            "i paid it",
            "i have paid",
            "i've paid",
        }

    # --------------------------------
    # Latest payment
    # --------------------------------

    async def handle_latest_payment(
        self,
        update: Update,
        customer_id: str,
    ):
        payment = self.stripe_service.get_latest_payment(
            customer_id
        )

        if not payment:
            await update.message.reply_text(
                "You don't have any payments."
            )
            return

        amount = payment.amount / 100
        currency = payment.currency.upper()

        await update.message.reply_text(
            f"Your latest payment was "
            f"{amount:,.2f} {currency} "
            f"({payment.status})."
        )

    # --------------------------------
    # Customer invoices
    # --------------------------------

    async def handle_invoices(
        self,
        update: Update,
        customer_id: str,
    ):
        invoices = (
            self.stripe_service
            .get_open_customer_invoices(customer_id)
        )

        if not invoices:
            await update.message.reply_text(
                "You don't have any open invoices."
            )
            return

        lines = ["Your open invoices:"]

        for invoice in invoices:
            amount = invoice.amount_due / 100
            currency = invoice.currency.upper()

            lines.append(
                f"- {invoice.id}: "
                f"{amount:,.2f} {currency} "
                f"({invoice.status})"
            )

        await update.message.reply_text(
            "\n".join(lines)
        )

    # --------------------------------
    # Pay invoice
    # --------------------------------

    async def handle_invoice_payment(
        self,
        update: Update,
        customer_id: str,
        message: str,
    ):
        """
        Find an open invoice belonging to the authenticated
        customer and provide Stripe's hosted invoice payment page.

        Customers can never pay an invoice belonging to
        another customer.
        """

        invoices = (
            self.stripe_service
            .get_open_customer_invoices(customer_id)
        )

        if not invoices:
            await update.message.reply_text(
                "You don't have any open invoices to pay."
            )
            return

        selected_invoice = None
        message_lower = message.lower()

        # --------------------------------
        # Try to identify invoice by amount
        # --------------------------------

        for invoice in invoices:
            amount = invoice.amount_due / 100
            amount_text = f"{amount:.2f}"

            if amount_text in message_lower:
                selected_invoice = invoice
                break

        # --------------------------------
        # If no amount specified,
        # use the first open invoice.
        # --------------------------------

        if selected_invoice is None:
            selected_invoice = invoices[0]

        amount = selected_invoice.amount_due
        amount_dollars = amount / 100
        currency = selected_invoice.currency.upper()

        # --------------------------------
        # Safety rule
        #
        # Payments >= $2,000 cannot be
        # completed by the Telegram bot.
        # --------------------------------

        if amount >= 200000:
            await update.message.reply_text(
                f"Your invoice is "
                f"${amount_dollars:,.2f} {currency}.\n\n"
                "Payments of $2,000 or more require "
                "business-owner approval and cannot "
                "be completed by this bot.\n\n"
                "Please contact the business owner "
                "to complete this payment."
            )
            return

        # --------------------------------
        # Stripe Hosted Invoice Page
        #
        # This is intentionally NOT a Payment Link.
        #
        # Paying this URL updates the actual
        # Stripe invoice to "paid".
        # --------------------------------

        if not selected_invoice.hosted_invoice_url:
            await update.message.reply_text(
                "This invoice does not currently have "
                "a payment page available."
            )
            return

        await update.message.reply_text(
            f"Your invoice is "
            f"${amount_dollars:,.2f} {currency}.\n\n"
            "You can securely pay it here:\n"
            f"{selected_invoice.hosted_invoice_url}"
        )

    # --------------------------------
    # Payment confirmation
    # --------------------------------

    async def handle_payment_confirmation(
        self,
        update: Update,
        customer_id: str,
    ):
        """
        The customer may say 'paid' after completing
        payment.

        We verify Stripe's current invoice state instead
        of trusting the customer's message.
        """

        invoices = (
            self.stripe_service
            .get_open_customer_invoices(customer_id)
        )

        if invoices:
            await update.message.reply_text(
                "Thanks. I still see an open invoice "
                "on Stripe. If you just completed the "
                "payment, please wait a few seconds and "
                "check again."
            )
            return

        await update.message.reply_text(
            "Your invoice is now paid. "
            "You have no open invoices."
        )

    # --------------------------------
    # Receipts
    # --------------------------------

    async def handle_receipts(
        self,
        update: Update,
        customer_id: str,
    ):
        """
        Show the customer's latest successful payment
        as a basic receipt summary.
        """

        payment = self.stripe_service.get_latest_payment(
            customer_id
        )

        if not payment:
            await update.message.reply_text(
                "You don't have any payment receipts yet."
            )
            return

        if payment.status != "succeeded":
            await update.message.reply_text(
                "I couldn't find a completed payment "
                "receipt for your account."
            )
            return

        amount = payment.amount / 100
        currency = payment.currency.upper()

        await update.message.reply_text(
            "Your latest payment receipt:\n\n"
            f"Payment ID: {payment.id}\n"
            f"Amount: {amount:,.2f} {currency}\n"
            f"Status: {payment.status}"
        )

    # --------------------------------
    # Run bot
    # --------------------------------

    def run(self):
        self.application.run_polling()

