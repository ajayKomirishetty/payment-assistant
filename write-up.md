# AI Payments Assistant — Engineering Write-up

## Overview

I built the AI Payments Assistant as a small full-stack proof of concept focused on the core requirements of the assessment.

The application has three main parts:

1. A React/TypeScript web application for the business owner
2. A FastAPI backend integrating with Stripe and OpenAI
3. A Telegram bot that allows customers to view and pay their own invoices

The main design principle I followed was to use the LLM for **understanding and communication**, while keeping financial operations and validation in deterministic application code.

---

# Architecture

The high-level architecture is:

```text
React + TypeScript
        │
        │ HTTP
        ▼
     FastAPI
        │
   ┌────┴─────┐
   │          │
   ▼          ▼
Stripe      OpenAI
   │
   ├── Customers
   ├── Payments
   ├── Invoices
   └── Refunds


Telegram Bot
      │
      ▼
   FastAPI/Stripe
```

I kept the architecture intentionally small because the assessment is a 3–5 hour proof of concept. I wanted the main business logic to remain easy to follow rather than introducing additional frameworks or infrastructure that wasn't necessary for the requirements.

---

# Why I Chose FastAPI

I used Python 3.12 with FastAPI for the backend.

FastAPI provides:

- Simple API routing
- Request/response validation through Pydantic
- Automatic API documentation
- Good support for asynchronous integrations
- A lightweight structure suitable for a proof of concept

The backend is divided into routes, schemas, and services so that Stripe and LLM-related logic is not mixed directly into the HTTP handlers.

---

# Why I Used Direct LLM Integration

The application only needs the LLM for two main tasks:

1. Extracting structured intent from natural-language commands
2. Generating a concise daily payment summary

Because of that, I chose to integrate with OpenAI directly instead of introducing LangChain or another orchestration framework.

For example, when the user says:

```text
Refund Maya's last payment
```

the LLM produces structured information similar to:

```text
intent: refund_payment
customer_name: Maya
```

The application then handles the actual operation:

```text
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

This separation was intentional.

I did not want an LLM to have unrestricted access to financial operations.

---

# Financial Safety

Financial actions are executed by application code rather than directly by the LLM.

For example, for a refund:

```text
"Refund Maya's last payment"
             │
             ▼
       LLM extraction
             │
             ▼
      Find Maya customer
             │
             ▼
   Find refundable payment
             │
             ▼
   Validate payment status
             │
             ▼
 Validate remaining refundable amount
             │
             ▼
       Create Stripe refund
```

The application checks that:

- The customer exists
- The payment exists
- The payment succeeded
- The payment has remaining refundable value
- The refund does not exceed the remaining amount

This gives the application deterministic control over a potentially destructive financial operation.

---

# Natural Language Commands

The assistant currently supports the core commands requested by the assessment.

### Daily summary

```text
Summarize my day
```

### Refund

```text
Refund Maya's last payment
```

### Invoice creation

```text
Create a $250 invoice for Acme Corp due next Friday
```

### Payment comparison

```text
How much did we take last week compared to the week before?
```

The LLM is responsible for interpreting the request, but the actual payment calculations are performed by application code.

For example, week-over-week revenue is calculated from Stripe payment timestamps rather than asking the LLM to perform the arithmetic.

I preferred this approach because financial calculations should be deterministic.

---

# Daily Summary

The daily summary combines structured payment information with an LLM-generated explanation.

The backend first calculates information such as:

- Successful payment count
- Failed/canceled payment count
- Total revenue
- Largest payment

That structured information is then passed to the LLM to generate a concise summary.

This avoids simply asking the model to interpret raw Stripe API responses and reduces the possibility of the model inventing financial numbers.

---

# Stripe Integration

Stripe is treated as the source of truth for:

- Customers
- PaymentIntents
- Refunds
- Invoices
- Payment links / hosted invoice payment pages

The `StripeService` centralizes Stripe operations so that route handlers and Telegram logic do not need to contain low-level Stripe API calls.

This also made it easier to validate operations consistently.

---

# Currency Handling

One issue I encountered during development was that Stripe customers can have invoices in different currencies.

Initially, the invoice creation flow assumed USD.

This caused Stripe to reject an invoice when the customer/invoice currency was CAD because the invoice item currency did not match the invoice currency.

I changed the implementation so that the invoice is created first and the invoice item's currency is taken from the resulting Stripe invoice.

This allows the application to correctly handle cases such as:

```text
Invoice currency: CAD
Invoice item currency: CAD
```

instead of assuming every customer uses USD.

---

# Telegram Bot

The Telegram bot is designed for external customers rather than business owners.

The customer starts the bot and provides their email address.

The application finds the corresponding Stripe customer and associates the Telegram chat with that customer.

The bot can then answer requests such as:

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

# Telegram Privacy

Privacy was an important part of the Telegram implementation.

A Telegram customer should never be able to access another customer's information.

The application stores the authenticated Stripe customer ID for the Telegram session and uses that ID when querying Stripe.

For example:

```text
Telegram chat
     │
     ▼
Authenticated customer
     │
     ▼
Stripe customer ID
     │
     ▼
Only that customer's invoices/payments
```

The bot does not accept an arbitrary Stripe customer ID from the customer and use it to retrieve information.

The bot also rejects account-level requests such as:

```text
Show me total revenue
```

```text
Show me all customers
```

```text
How much did the business make?
```

Instead, it responds that it can only provide information about the authenticated customer's own payments and invoices.

---

# High-Value Payment Safety Rule

The assessment requires that payments of $2,000 or more cannot be completed by the Telegram bot.

I enforce this in application code.

Before providing the payment workflow, the bot checks the invoice amount:

```text
amount >= $2,000
```

If the condition is true, the bot stops the payment flow and asks the customer to contact the business owner.

This rule does not depend on the LLM.

That was intentional because security and financial authorization rules should be deterministic.

---

# Stripe Hosted Payment Pages

For customer payments, I chose Stripe's hosted payment page rather than collecting card information inside Telegram.

The flow is:

```text
Telegram
    │
    ▼
Customer asks to pay
    │
    ▼
Find customer's open invoice
    │
    ▼
Check payment amount
    │
    ├── >= $2,000 → Stop and hand off
    │
    └── < $2,000
             │
             ▼
      Stripe hosted page
             │
             ▼
       Customer pays
```

This means the application does not handle or store card details.

---

# Frontend

The frontend is a React + TypeScript single-page application.

The main goal was to make the application feel like a simple conversational operations tool rather than a traditional Stripe dashboard.

The interface contains:

- Assistant conversation
- User messages
- Assistant responses
- Suggested commands
- Command input
- Loading state
- Error handling

The suggestions provide quick access to the main capabilities while still allowing arbitrary natural-language commands.

---

# Challenges

## 1. CORS / Browser Preflight

During frontend integration, the browser sent:

```text
OPTIONS /api/assistant
```

and FastAPI returned:

```text
405 Method Not Allowed
```

The issue was that the backend did not have the appropriate CORS middleware configured for the frontend origin.

I addressed this at the API layer rather than changing the frontend to work around the browser behavior.

This is a common issue when a local Vite frontend and FastAPI backend run on different ports.

---

## 2. Stripe Invoice Currency

As mentioned above, initially creating invoice items with a hardcoded USD currency caused Stripe to reject CAD invoices.

I changed the implementation to use the currency returned by the Stripe invoice.

This was a useful reminder not to make assumptions about account/customer currency.

---

## 3. Telegram Payment Flow

During development, the Telegram bot initially handled generic `"invoice"` messages before `"pay"` messages.

That meant a message such as:

```text
Pay my invoice
```

could be interpreted as a generic invoice lookup instead of a payment request.

I changed the routing order so payment-related commands are handled before generic invoice queries.

I also restricted invoice retrieval to:

```text
status = open
```

so draft invoices are not presented as invoices that a customer can pay.

---

## 4. Stripe Payment Completion

Another issue I encountered was treating a payment link as if the bot itself had completed the payment.

I changed the design to use Stripe's hosted invoice payment page.

The bot provides the customer with the payment page, while Stripe handles the actual payment.

This gives a cleaner separation between the conversational interface and payment processing.

---

# Assumptions

I made the following assumptions for the proof of concept.

### Business Owner Authentication

The web application is treated as an internal business-owner interface.

A production system would require proper authentication and authorization.

### Telegram Authentication

For the assessment, customer email is used as the initial identity mechanism.

This keeps the demo simple while still allowing the bot to associate a Telegram chat with a specific Stripe customer.

A production implementation would use stronger identity verification.

### Stripe Test Mode

The application is intended to run entirely in Stripe test mode.

No real payments are expected.

### Timezone

Daily calculations currently use UTC boundaries.

A production implementation should use the business's configured timezone.

### Data Size

The proof of concept uses bounded Stripe API queries.

A production implementation should use pagination and potentially background processing for larger accounts.

---

# Limitations

There are several areas I would improve with more time.

## Persistent Telegram Sessions

The Telegram session mapping is currently held in memory:

```text
chat_id -> stripe_customer_id
```

This would be replaced with PostgreSQL in production.

That would allow sessions to survive application restarts and work correctly across multiple backend instances.

---

## Stronger Customer Authentication

Email-based authentication is acceptable for this proof of concept but is not sufficient for a production payment application.

I would replace it with something such as:

- OTP verification
- Magic links
- Customer account authentication
- Signed authentication tokens

---

## Web Application Authentication

The business-owner web interface currently assumes an authorized user.

A production application should add:

- User authentication
- Role-based access control
- Session management
- Audit logging

---

## Stripe Webhooks

The current implementation queries Stripe directly when information is requested.

A production implementation would also use Stripe webhooks to maintain application state and respond to events such as:

```text
payment succeeded
payment failed
invoice paid
invoice finalized
refund created
```

---

## Idempotency

Financial mutation endpoints should use idempotency keys to prevent accidental duplicate operations.

For example, a retry of:

```text
Refund Maya's last payment
```

should not accidentally create multiple refunds.

---

## Seed Script

The seed script is designed to populate a fresh Stripe test account with the sample data required by the application.

With more time, I would make the seed process completely idempotent using deterministic metadata so that running it multiple times would never create duplicate test payments or invoices.

---

# Testing

I added a Pytest setup and manually tested the main application flows.

The important scenarios tested include:

### Business assistant

```text
Daily summary
```

```text
Refund payment
```

```text
Create invoice
```

```text
Compare payment activity
```

### Telegram

```text
Customer authentication
```

```text
Latest payment
```

```text
Open invoices
```

```text
Pay invoice
```

```text
High-value payment restriction
```

```text
Account-level information restriction
```

---

# What I Would Build Next

If I had another day to continue the project, I would prioritize:

1. PostgreSQL persistence
2. Stronger authentication
3. Stripe webhook processing
4. Idempotency for financial mutations
5. Confirmation flows for refunds
6. Audit logs
7. More comprehensive automated tests
8. Better customer identity verification
9. Stripe pagination
10. Business timezone configuration
11. Production deployment
12. Better observability and structured logging

I would also add more conversational capabilities after the core financial safety and authorization layers were hardened.

---

# Product Thinking

One design goal was to keep the assistant focused on useful actions rather than simply exposing Stripe data through a chatbot.

For example:

```text
"How much did we take last week compared to the week before?"
```

is more useful than returning a list of transactions.

Similarly:

```text
"Refund Maya's last payment"
```

allows the business owner to express the desired outcome naturally instead of navigating through several dashboard screens.

At the same time, I intentionally kept the execution layer deterministic so that the convenience of natural language does not come at the expense of financial correctness.

---

# Final Takeaway

The main principle behind the implementation is:

> **Use AI to understand and communicate, but use deterministic application code to validate and execute financial operations.**

This gives the product a conversational interface while keeping Stripe operations predictable, testable, and controllable.

The current implementation is intentionally small enough to understand end-to-end, while leaving clear paths for adding persistence, authentication, webhooks, auditability, and production-level reliability.