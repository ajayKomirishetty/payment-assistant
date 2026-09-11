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
        # PostgreSQL will replace this later.
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
        # --------------------------------

        restricted_terms = [
            "revenue",
            "total revenue",
            "business revenue",
            "company revenue",
            "all customers",
            "other customers",
            "total payments",
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
        # Check this BEFORE generic invoice
        # handling.
        # --------------------------------

        if "pay" in message_lower:
            await self.handle_invoice_payment(
                update,
                customer_id,
                message,
            )
            return

        # --------------------------------
        # Payments
        # --------------------------------

        if "payment" in message_lower:
            payment = self.stripe_service.get_latest_payment(
                customer_id
            )

            if not payment:
                await update.message.reply_text(
                    "You don't have any payments."
                )
                return

            amount = payment.amount / 100

            await update.message.reply_text(
                f"Your latest payment was "
                f"${amount:,.2f} "
                f"({payment.status})."
            )

            return

        # --------------------------------
        # Invoices
        # --------------------------------

        if "invoice" in message_lower:
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

                lines.append(
                    f"- {invoice.id}: "
                    f"${amount:,.2f} "
                    f"({invoice.status})"
                )

            await update.message.reply_text(
                "\n".join(lines)
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
            "• Pay my invoice"
        )

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

      # If the customer mentions an amount, try to match it.
      for invoice in invoices:
          amount = invoice.amount_due / 100
          amount_text = f"{amount:.2f}"

          if amount_text in message_lower:
              selected_invoice = invoice
              break

      # If no amount was specified, use the first open invoice.
      if selected_invoice is None:
          selected_invoice = invoices[0]

      amount = selected_invoice.amount_due
      amount_dollars = amount / 100

      # Safety rule from the assignment.
      if amount >= 200000:
          await update.message.reply_text(
              f"Your invoice is ${amount_dollars:,.2f} "
              f"{selected_invoice.currency.upper()}.\n\n"
              "Payments of $2,000 or more require business-owner "
              "approval and cannot be completed by this bot.\n\n"
              "Please contact the business owner to complete the payment."
          )
          return

      # Use Stripe's actual invoice payment page.
      if not selected_invoice.hosted_invoice_url:
          await update.message.reply_text(
              "This invoice does not currently have a payment page available."
          )
          return

      await update.message.reply_text(
          f"Your invoice is ${amount_dollars:,.2f} "
          f"{selected_invoice.currency.upper()}.\n\n"
          "You can securely pay it here:\n"
          f"{selected_invoice.hosted_invoice_url}"
      )

    def run(self):
        self.application.run_polling()