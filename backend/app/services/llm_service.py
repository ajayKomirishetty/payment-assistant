from datetime import date

from openai import OpenAI

from app.core.config import settings
from app.schemas.assistant import PaymentCommand


class LLMService:
    def __init__(self):
        if not settings.openai_api_key:
            raise ValueError(
                "OPENAI_API_KEY is not configured."
            )

        self.client = OpenAI(
            api_key=settings.openai_api_key
        )

    def parse_command(self, message: str) -> PaymentCommand:
        today = date.today().isoformat()

        system_prompt = f"""
You are the command interpreter for a payment assistant.

Today's date is {today}.

Convert the user's natural-language request into a
structured payment command.

Supported intents:

1. refund_payment
   Examples:
   - Refund Maya's latest payment
   - Refund Maya's last payment

2. create_invoice
   Examples:
   - Create a $250 invoice for Acme Corp
   - Invoice Acme Corp for $500 due next Friday

3. payment_comparison
   Examples:
   - How much did we take last week compared to the week before?
   - Compare this week's payments with last week

4. daily_summary
   Examples:
   - Give me today's payment summary
   - Summarize today's payments

Rules:

- Extract the customer name when applicable.
- Extract the amount in dollars.
- Resolve relative dates such as "next Friday"
  using today's date.
- Do not invent missing information.
- Use null when a field is not applicable.
- "latest payment" and "last payment" mean the customer's
  most recent payment.
"""

        response = self.client.responses.parse(
            model="gpt-5.6-luna",
            input=[
                {
                    "role": "system",
                    "content": system_prompt,
                },
                {
                    "role": "user",
                    "content": message,
                },
            ],
            text_format=PaymentCommand,
        )

        if response.output_parsed is None:
            raise ValueError(
                "The AI could not understand the request."
            )

        return response.output_parsed
    
    def generate_daily_summary(
    self,
    payment_summary: dict,
    ) -> str:
        prompt = f"""
    You are a payment business assistant.

    Create a concise daily payment summary based ONLY
    on the verified payment data below.

    Payment data:
    - Successful payments:
      {payment_summary["successful_payment_count"]}
    - Failed payments:
      {payment_summary["failed_payment_count"]}
    - Total revenue:
      ${payment_summary["total_revenue"] / 100:.2f}
    - Largest payment:
      {payment_summary["largest_payment"]}

    Rules:
    - Do not invent facts.
    - Do not calculate different numbers.
    - Mention the total revenue.
    - Mention successful and failed payment activity.
    - Mention the largest payment if one exists.
    - Keep the response to 2-4 sentences.
    - Sound like a useful business assistant, not a report.
    """

        response = self.client.responses.create(
            model="gpt-5.6-luna",
            input=prompt,
        )

        return response.output_text.strip()