# Replicant Payments Assistant

An AI-powered payments operations assistant built as a take-home assessment for Replicant.

The application provides:

- A web-based AI payments assistant for business owners
- Natural-language payment operations
- Stripe payment and invoice management
- Daily payment summaries generated with an LLM
- Week-over-week payment comparison
- Payment refunds
- Invoice creation
- A privacy-preserving Telegram customer payment bot
- Stripe-hosted payment pages
- Safety controls for high-value customer payments

---

## Architecture

```text
                         ┌─────────────────────────┐
                         │        React UI          │
                         │     TypeScript/Vite      │
                         └────────────┬────────────┘
                                      │
                                      │ HTTP
                                      ▼
                         ┌─────────────────────────┐
                         │       FastAPI API       │
                         │                         │
                         │  AssistantService      │
                         │  StripeService          │
                         │  LLMService             │
                         └───────┬─────────┬───────┘
                                 │         │
                    ┌────────────┘         └─────────────┐
                    ▼                                    ▼
          ┌──────────────────┐                  ┌─────────────────┐
          │      Stripe      │                  │     OpenAI      │
          │                  │                  │                 │
          │ Payments         │                  │ Intent parsing  │
          │ Customers        │                  │ Summaries       │
          │ Invoices         │                  │                 │
          │ Refunds          │                  │                 │
          └──────────────────┘                  └─────────────────┘


                         ┌─────────────────────────┐
                         │     Telegram Bot        │
                         │                         │
                         │ Customer authentication │
                         │ Own invoices/payments   │
                         │ Payment workflow        │
                         └────────────┬────────────┘
                                      │
                                      ▼
                               ┌──────────────┐
                               │    Stripe    │
                               └──────────────┘
```

---

# Technology Stack

## Backend

- Python 3.12
- FastAPI
- Stripe Python SDK
- OpenAI API
- Pydantic
- python-dotenv / pydantic-settings
- Python Telegram Bot
- Pytest

## Frontend

- React
- TypeScript
- Vite
- CSS

## External Services

- Stripe Test Mode
- OpenAI
- Telegram Bot API

---

# Project Structure

```text
replicant-payments-assistant/
│
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   │
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   └── routes/
│   │   │       ├── __init__.py
│   │   │       ├── health.py
│   │   │       ├── assistant.py
│   │   │       ├── payments.py
│   │   │       ├── invoices.py
│   │   │       └── customers.py
│   │   │
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   └── config.py
│   │   │
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   ├── assistant.py
│   │   │   └── invoice.py
│   │   │
│   │   └── services/
│   │       ├── __init__.py
│   │       ├── stripe_service.py
│   │       ├── assistant_service.py
│   │       ├── llm_service.py
│   │       └── telegram_service.py
│   │
│   ├── tests/
│   ├── seed.py
│   ├── telegram_bot.py
│   ├── .env
│   ├── .env.example
│   └── .gitignore
│
├── frontend/
│   ├── src/
│   ├── public/
│   ├── package.json
│   ├── tsconfig.json
│   ├── vite.config.ts
│   └── ...
│
├── README.md
├── write-up.md
├── .gitignore
└── .env.example
```

---

# Prerequisites

Install the following before starting:

- Python 3.12+
- Node.js 18+
- npm
- Stripe account
- Stripe test API key
- OpenAI API key
- Telegram bot token

Everything in this project should be run against Stripe **test mode**.

No real money should be involved.

---

# 1. Clone the Repository

```bash
git clone https://github.com/ajayKomirishetty/replicant-payment-assistant
cd replicant-payments-assistant
```

---

# 2. Backend Setup

Move into the backend directory:

```bash
cd backend
```

Create a Python virtual environment:

```bash
python3.12 -m venv .venv
```

Activate it:

### macOS / Linux

```bash
source .venv/bin/activate
```

### Windows

```powershell
.venv\Scripts\activate
```

Verify Python:

```bash
python --version
```

Expected:

```text
Python 3.12.x
```

---

# 3. Install Backend Dependencies

Upgrade pip:

```bash
python -m pip install --upgrade pip
```

Install application dependencies:

```bash
python -m pip install fastapi "uvicorn[standard]" stripe python-dotenv pydantic-settings openai python-telegram-bot
```

Install test dependencies:

```bash
python -m pip install pytest
```

Alternatively, if a `requirements.txt` file is provided:

```bash
python -m pip install -r requirements.txt
```

---

# 4. Environment Variables

Create:

```text
backend/.env
```

Example:

```env
STRIPE_SECRET_KEY=sk_test_...
OPENAI_API_KEY=sk-...
TELEGRAM_BOT_TOKEN=...
```

Do not commit `.env` to Git.

The repository includes `.env.example` as a template.

---

# 5. Stripe Setup

Create or use a Stripe account in **test mode**.

The application expects a Stripe test secret key:

```text
STRIPE_SECRET_KEY=sk_test_...
```

Stripe test mode is important because this application creates payments, invoices, refunds, and payment links.

No real payments should be made.

---

# 6. OpenAI Setup

Set:

```env
OPENAI_API_KEY=your_openai_api_key
```

The application uses the LLM for:

1. Natural-language command interpretation
2. Daily payment summary generation

The LLM is not responsible for directly executing financial operations.

Instead, the architecture is:

```text
User message
     │
     ▼
LLM
     │
     │ structured command
     ▼
Python validation
     │
     ▼
Stripe API
```

This keeps financial actions deterministic and separates interpretation from execution.

---

# 7. Telegram Setup

Create a Telegram bot using BotFather.

Set the token:

```env
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
```

The Telegram bot is intended for customers rather than business administrators.

Customers authenticate using their Stripe customer email.

The bot only accesses the Stripe customer associated with the authenticated Telegram session.

---

# 8. Seed the Stripe Test Account

From:

```text
backend/
```

run:

```bash
python seed.py
```

The seed script creates the sample Stripe data required by the application.

The sample data includes customers such as:

- Maya Johnson
- Acme Corp
- John Smith
- Sarah Williams

It also creates test payment activity and invoices.

The seed script uses Stripe test mode.

---

# 9. Running the Backend

From:

```text
backend/
```

activate the virtual environment:

```bash
source .venv/bin/activate
```

Start FastAPI:

```bash
uvicorn app.main:app --reload
```

The backend will normally be available at:

```text
http://localhost:8000
```

FastAPI documentation:

```text
http://localhost:8000/docs
```

---

# 10. Backend API

## Health Check

```http
GET /health
```

Example:

```bash
curl http://localhost:8000/health
```

---

## List Payments

```http
GET /api/payments
```

Example:

```bash
curl http://localhost:8000/api/payments
```

---

## Refund Payment

```http
POST /api/payments/{payment_id}/refund
```

Example:

```bash
curl -X POST \
  http://localhost:8000/api/payments/pi_xxx/refund
```

---

## List Customers

```http
GET /api/customers
```

Example:

```bash
curl http://localhost:8000/api/customers
```

---

## Get Customer

```http
GET /api/customers/{name_or_email}
```

Example:

```bash
curl http://localhost:8000/api/customers/Maya%20Johnson
```

---

## Get Customer's Latest Payment

```http
GET /api/customers/{name_or_email}/latest-payment
```

Example:

```bash
curl http://localhost:8000/api/customers/Maya%20Johnson/latest-payment
```

---

## List Invoices

```http
GET /api/invoices
```

Example:

```bash
curl http://localhost:8000/api/invoices
```

---

## Create Invoice

```http
POST /api/invoices
```

Example:

```bash
curl -X POST \
  http://localhost:8000/api/invoices \
  -H "Content-Type: application/json" \
  -d '{
    "customer": "Acme Corp",
    "amount": 25000,
    "description": "Test invoice",
    "days_until_due": 7
  }'
```

The API accepts the invoice amount in cents.

For example:

```text
25000 = $250.00
```

---

# 11. AI Assistant API

The main assistant endpoint is:

```http
POST /api/assistant
```

Request:

```json
{
  "message": "Refund Maya's last payment"
}
```

Example:

```bash
curl -X POST \
  http://localhost:8000/api/assistant \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Refund Maya'\''s last payment"
  }'
```

The assistant extracts the user's intent and relevant information.

Supported intents include:

```text
refund_payment
create_invoice
payment_comparison
daily_summary
```

---

# 12. Example Assistant Commands

## Daily Summary

```text
Summarize my day
```

or:

```text
How did payments look today?
```

The backend retrieves today's payment activity and sends the structured payment information to the LLM.

The LLM generates a concise natural-language summary.

---

## Refund

```text
Refund Maya's last payment
```

The LLM identifies:

```text
intent = refund_payment
customer = Maya Johnson
```

Python then:

1. Finds Maya's Stripe customer
2. Finds her latest refundable payment
3. Validates that the payment succeeded
4. Checks the remaining refundable amount
5. Creates the Stripe refund

The LLM does not execute the refund itself.

---

## Create Invoice

```text
Create a $250 invoice for Acme Corp due next Friday
```

The LLM extracts:

```text
intent = create_invoice
customer = Acme Corp
amount = 250
due_date = next Friday
```

Python then validates the information and creates the Stripe invoice.

---

## Compare Payments

```text
How much did we take last week compared to the week before?
```

The backend calculates the payment totals deterministically from Stripe data.

The calculation is not delegated to the LLM.

Example:

```text
We took $7,570.00 this week compared with $0.00 last week — no previous-week revenue to compare against.
```

---

# 13. Frontend Setup

Open a second terminal.

From the project root:

```bash
cd frontend
```

Install dependencies:

```bash
npm install
```

Start the development server:

```bash
npm run dev
```

Vite will display the local frontend URL.

Typically:

```text
http://localhost:5173
```

The frontend communicates with:

```text
http://localhost:8000
```

for the FastAPI backend.

---

# 14. Frontend Usage

The frontend provides a chatbot-style interface.

Example commands:

```text
Summarize my day
```

```text
Refund Maya's last payment
```

```text
Create a $250 invoice for Acme Corp due next Friday
```

```text
How much did we take last week compared to the week before?
```

The UI displays:

- User messages
- Assistant responses
- Suggested commands
- Loading state
- Error messages

---

# 15. Telegram Bot

The Telegram bot runs separately from FastAPI.

From:

```text
backend/
```

activate the virtual environment:

```bash
source .venv/bin/activate
```

Run:

```bash
python telegram_bot.py
```

The bot starts polling Telegram.

---

# 16. Telegram Customer Authentication

A customer starts the bot with:

```text
/start
```

The bot asks for the customer's email.

For example:

```text
maya@example.com
```

The application looks up the Stripe customer by email.

After successful authentication, the Telegram chat is associated with the Stripe customer.

The customer can then ask:

```text
What is my latest payment?
```

```text
Show my invoices
```

```text
Pay my invoice
```

---

# 17. Telegram Privacy Model

The Telegram bot intentionally has a more restricted permission model than the business-owner web assistant.

A customer can only access:

```text
Their own payments
Their own invoices
Their own payment links
```

The customer cannot access:

```text
Other customers
Other customers' invoices
Other customers' payments
Business revenue
Total account revenue
Account-level financial information
```

Customer-specific Stripe IDs are obtained from the authenticated session rather than being accepted directly from user input.

For example, the bot does not allow a customer to provide:

```text
cus_other_customer
```

and retrieve that customer's information.

---

# 18. Telegram Payment Workflow

A customer can ask:

```text
Pay my invoice
```

The bot retrieves only open invoices belonging to the authenticated customer.

If there is an open invoice, the bot provides Stripe's hosted invoice payment page.

Example:

```text
Your invoice is $250.00 CAD.

You can securely pay it here:

https://invoice.stripe.com/...
```

The payment itself is completed through Stripe's hosted payment page.

The Telegram bot does not collect or store card information.

---

# 19. $2,000 Payment Safety Rule

The assessment requires that payments of $2,000 or more cannot be completed by the Telegram bot.

The bot therefore checks the invoice amount before providing a payment workflow.

For example:

```text
Your invoice is $2,500.00 CAD.

Payments of $2,000 or more require business-owner approval
and cannot be completed by this bot.

Please contact the business owner to complete the payment.
```

This rule is enforced in application code rather than relying on the LLM.

---

# 20. Security Principles

The project intentionally separates AI interpretation from financial execution.

The LLM can determine:

```text
What is the user asking for?
```

But it cannot directly perform:

```text
Stripe refund
Stripe payment
Stripe invoice creation
```

Instead:

```text
User
  ↓
LLM
  ↓
Structured command
  ↓
Application validation
  ↓
StripeService
  ↓
Stripe
```

This makes it possible to apply deterministic validation around financial actions.

Examples include:

- Customer must exist
- Payment must be refundable
- Refund cannot exceed the remaining refundable amount
- Invoice amount must be positive
- Invoice due date must be in the future
- Telegram customer must be authenticated
- Telegram customer can only access their own Stripe resources
- Telegram payments >= $2,000 are blocked

---

# 21. Currency Handling

The application does not assume that every Stripe customer uses USD.

For example, a customer may have an invoice in CAD.

When creating an invoice, the application uses the Stripe invoice's currency when creating its invoice item.

This prevents Stripe errors caused by mixing currencies on a single invoice.

For example:

```text
Invoice currency: CAD
Invoice item currency: CAD
```

---

# 22. Testing

Run tests from the backend directory:

```bash
cd backend
source .venv/bin/activate
python -m pytest
```

For verbose output:

```bash
python -m pytest -v
```

---

# 23. Manual End-to-End Test

A basic end-to-end test can be performed in the following order.

## Step 1

Start the backend:

```bash
cd backend
source .venv/bin/activate
uvicorn app.main:app --reload
```

## Step 2

Start the frontend in another terminal:

```bash
cd frontend
npm run dev
```

## Step 3

Open the frontend.

Try:

```text
Summarize my day
```

## Step 4

Try:

```text
How much did we take last week compared to the week before?
```

## Step 5

Try:

```text
Refund Maya's last payment
```

## Step 6

Try:

```text
Create a $250 invoice for Acme Corp due next Friday
```

## Step 7

Start Telegram:

```bash
cd backend
source .venv/bin/activate
python telegram_bot.py
```

## Step 8

Open the Telegram bot.

Send:

```text
/start
```

Then authenticate using a seeded customer email.

For example:

```text
maya@example.com
```

Then try:

```text
What is my latest payment?
```

```text
Show my invoices
```

```text
Pay my invoice
```

---

# 24. Repository Setup

The project intentionally uses a single repository containing both applications.

```text
replicant-payments-assistant/
├── backend/
├── frontend/
├── README.md
└── write-up.md
```

This makes the take-home easier to evaluate because the complete system is contained in one repository.

---

# 25. Environment Files

The repository should contain:

```text
.env.example
```

but should not contain real credentials.

For example:

```env
STRIPE_SECRET_KEY=
OPENAI_API_KEY=
TELEGRAM_BOT_TOKEN=
```

The real:

```text
.env
```

must remain ignored by Git.

---

# 26. Important Git Checks Before Submission

From the project root:

```bash
git status
```

Make sure secrets are not tracked.

Check:

```bash
git ls-files | grep ".env"
```

You should not see your real `.env` file.

Check that virtual environments are ignored:

```bash
git status --ignored
```

The following should not be committed:

```text
backend/.venv/
frontend/node_modules/
.env
```

---

# 27. Recommended `.gitignore`

The repository should ignore at least:

```gitignore
# Environment
.env
.env.*
!.env.example

# Python
__pycache__/
*.py[cod]
.pytest_cache/
.venv/
venv/
*.egg-info/

# Node
node_modules/
dist/

# macOS
.DS_Store

# IDE
.idea/
.vscode/
```

---

# 28. Design Decisions

## Why FastAPI?

FastAPI provides a small, straightforward API layer with:

- Type validation
- Automatic API documentation
- Async support
- Simple route organization
- Good fit for an AI/Stripe integration

The assessment is a proof of concept, so a lightweight backend was preferable to introducing unnecessary infrastructure.

---

## Why React + TypeScript?

The frontend is a single-page chatbot application.

React provides a simple component model while TypeScript provides stronger type safety around API responses and UI state.

---

## Why direct OpenAI integration?

The application only requires a small number of LLM operations:

1. Structured command extraction
2. Daily summary generation

Using the OpenAI API directly keeps the implementation simple and makes the control flow explicit.

A framework such as LangChain or LangGraph was not necessary for this proof of concept.

---

## Why Stripe-hosted payment pages?

The Telegram bot does not collect card information.

Instead, it provides Stripe's hosted payment page.

This keeps payment handling inside Stripe and reduces the amount of sensitive payment data handled by the application.

---

# 29. Known Limitations

This is intentionally a proof of concept.

Some areas that would be improved for production include:

### Persistent Telegram Sessions

The current Telegram authentication mapping is stored in memory.

```text
chat_id -> stripe_customer_id
```

A production implementation would persist this relationship in PostgreSQL.

This would allow sessions to survive application restarts and support multiple application instances.

---

### Customer Authentication

The demo authenticates Telegram users using their customer email.

A production implementation should use a stronger identity verification mechanism, such as:

- Magic link
- OTP
- Verified customer account
- Signed customer token
- Stripe Customer Portal authentication

---

### Seed Idempotency

The seed script is designed for a fresh Stripe test account.

A production-quality seed system would use deterministic metadata or identifiers to make repeated executions completely idempotent.

---

### Business Timezone

Daily summaries currently use UTC boundaries.

A production implementation should use the business's configured timezone.

---

### Pagination

Some Stripe queries use bounded limits for the proof of concept.

A production system should implement Stripe pagination when processing larger accounts.

---

### Authorization

The web assistant is designed as the business-owner interface.

A production implementation would add explicit authentication and authorization around the business-owner API.

---

### Natural Language Coverage

The LLM command parser currently supports the core commands required by the assessment.

A production implementation could support more flexible commands such as:

```text
Refund the payment Maya made yesterday
```

```text
Create an invoice for Acme for $500 CAD due in 30 days
```

```text
Show me failed payments from this month
```

---

# 30. Future Improvements

With more development time, I would add:

1. PostgreSQL persistence
2. Proper business-owner authentication
3. Role-based authorization
4. Idempotency keys for financial mutations
5. Stripe webhook processing
6. Persistent Telegram customer sessions
7. Better customer verification
8. Audit logs for financial operations
9. Confirmation steps before destructive actions
10. More comprehensive automated tests
11. Stripe pagination
12. Configurable business timezone
13. Observability and structured logging
14. Rate limiting
15. More detailed payment analytics
16. Production deployment configuration

---

# 31. Financial Safety Model

Financial mutations are intentionally protected by application-level validation.

For example, for a refund:

```text
User:
"Refund Maya's last payment"

        ↓

LLM extracts:
intent = refund_payment
customer = Maya

        ↓

Application:
Find Maya
        ↓
Find latest refundable payment
        ↓
Verify payment succeeded
        ↓
Verify remaining refundable amount
        ↓
Create Stripe refund
```

The LLM never receives unrestricted access to Stripe.

---

# 32. Assessment Requirements Coverage

| Requirement | Implementation |
|---|---|
| Backend server | FastAPI |
| Stripe integration | Stripe Python SDK |
| LLM integration | OpenAI API |
| Daily summary | Implemented |
| Natural language commands | Implemented |
| Refund payment | Implemented |
| Create invoice | Implemented |
| Payment comparison | Implemented |
| React SPA | Implemented |
| Chatbot interface | Implemented |
| Telegram bot | Implemented |
| Customer-specific access | Implemented |
| Privacy restrictions | Implemented |
| $2,000 payment restriction | Implemented |
| Stripe payment workflow | Implemented |
| Seed script | Implemented |
| Automated tests | Pytest |
| Architecture documentation | This README |
| Assumptions/challenges/limitations | `write-up.md` |

---

# 33. Quick Start

For an evaluator, the shortest path is:

## Terminal 1 — Backend

```bash
cd backend

python3.12 -m venv .venv
source .venv/bin/activate

python -m pip install --upgrade pip
python -m pip install fastapi "uvicorn[standard]" stripe python-dotenv pydantic-settings openai python-telegram-bot pytest

# Configure .env first

python seed.py

uvicorn app.main:app --reload
```

---

## Terminal 2 — Frontend

```bash
cd frontend

npm install
npm run dev
```

---

## Terminal 3 — Telegram

```bash
cd backend

source .venv/bin/activate

python telegram_bot.py
```

---

# 34. Final Notes

This project is designed as a small but complete proof of concept.

The main architectural principle is:

> Use AI for interpretation and communication, but keep financial operations deterministic and controlled by application code.

Stripe remains the source of truth for payments, invoices, refunds, and customer financial data.

The web assistant is designed for the business owner, while the Telegram bot is deliberately restricted to the authenticated customer's own financial information.
