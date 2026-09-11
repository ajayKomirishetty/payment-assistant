# Replicant Payments Assistant — Frontend

React + TypeScript frontend for the Replicant AI Payments Assistant.

This application provides a chatbot-style interface for the business owner to interact with the payments assistant using natural-language commands.

## Features

- Conversational payments assistant
- Natural-language commands
- Daily payment summaries
- Payment comparisons
- Customer payment refunds
- Invoice creation
- Suggested commands
- Loading and error states
- Responsive chat interface

## Tech Stack

- React
- TypeScript
- Vite
- CSS
- Fetch API

The frontend communicates with the FastAPI backend.

```text
React / TypeScript
        │
        │ HTTP
        ▼
FastAPI Backend
        │
        ├── Stripe
        └── OpenAI
```

## Requirements

- Node.js 18+
- npm
- Running FastAPI backend

## Installation

From this directory:

```bash
npm install
```

## Development

Start the frontend development server:

```bash
npm run dev
```

Vite will provide the local development URL, typically:

```text
http://localhost:5173
```

Make sure the backend is also running:

```bash
cd ../backend

source .venv/bin/activate

uvicorn app.main:app --reload
```

The backend normally runs at:

```text
http://localhost:8000
```

## Example Commands

The assistant supports natural-language requests such as:

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

## API

The frontend sends assistant requests to:

```text
POST http://localhost:8000/api/assistant
```

Example request:

```json
{
  "message": "Refund Maya's last payment"
}
```

The backend handles:

- Natural-language interpretation
- Validation
- Stripe operations
- Financial calculations
- LLM-generated responses

The frontend is intentionally kept responsible for presentation and user interaction rather than financial business logic.

## Production Build

Create a production build:

```bash
npm run build
```

Preview the production build locally:

```bash
npm run preview
```

## Project Structure

```text
frontend/
├── public/
├── src/
│   ├── assets/
│   ├── App.tsx
│   ├── App.css
│   ├── index.css
│   └── main.tsx
├── package.json
├── tsconfig.json
├── vite.config.ts
└── README.md
```

## Design Approach

The frontend is intentionally designed as a focused conversational interface rather than a traditional payments dashboard.

The business owner can describe an action in natural language and receive the result directly in the conversation.

The UI also provides suggested commands for the most common workflows, making the primary capabilities discoverable without requiring the user to know specific commands.

## Separation of Responsibilities

The frontend does not directly communicate with Stripe.

```text
User
  ↓
React UI
  ↓
FastAPI
  ↓
AssistantService
  ↓
StripeService / LLMService
  ↓
Stripe / OpenAI
```

This keeps Stripe credentials and financial operations on the backend.