from fastapi import FastAPI

from app.api.routes.assistant import router as assistant_router
from app.api.routes.customers import router as customers_router
from app.api.routes.health import router as health_router
from app.api.routes.invoices import router as invoices_router
from app.api.routes.payments import router as payments_router


app = FastAPI(
    title="Replicant Payments Assistant",
    version="1.0.0",
)


app.include_router(health_router)
app.include_router(payments_router)
app.include_router(invoices_router)
app.include_router(customers_router)
app.include_router(assistant_router)