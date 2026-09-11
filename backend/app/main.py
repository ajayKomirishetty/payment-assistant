from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.health import router as health_router
from app.api.routes.payments import router as payments_router
from app.api.routes.invoices import router as invoices_router
from app.api.routes.customers import router as customers_router
from app.api.routes.assistant import router as assistant_router


app = FastAPI(
    title="Replicant Payments Assistant",
    description="AI-powered payments assistant",
    version="1.0.0",
)


# --------------------------------
# CORS
# --------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --------------------------------
# Routes
# --------------------------------

app.include_router(health_router)
app.include_router(payments_router)
app.include_router(invoices_router)
app.include_router(customers_router)
app.include_router(assistant_router)