from datetime import datetime, timezone

from fastapi import FastAPI

from app.core.settings import settings

from app.api.auth import router as auth_router
from app.api.kiosk import router as kiosk_router
from app.api.documents import router as documents_router
from app.api.print_jobs import router as print_jobs_router
from app.api.billing import router as billing_router
from app.api.payment import router as payment_router
from app.api.print_queue import router as print_queue_router
from app.api.inventory_pricing import router as inventory_pricing_router
from app.api.customer_sessions import router as customer_sessions_router
from app.api.customer_uploads import router as customer_uploads_router
from app.api.customer_print_jobs import router as customer_print_jobs_router
from app.api.customer_payments import router as customer_payments_router
from app.api.admin_dashboard import router as admin_dashboard_router
from app.api.admin_management import router as admin_management_router
from app.api.kiosk_display import router as kiosk_display_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Scalable backend server for the PayPrint ecosystem.",
)

# Development CORS: local frontend via VS Code Live Server
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500",
        "http://127.0.0.1:5501",
        "http://localhost:5501",
        "http://10.232.196.179:5501",
	"http://127.0.0.1:5502",
	"http://localhost:5502",
        "http://10.232.196.179:5502",
        "http://127.0.0.1:5505",
        "http://localhost:5505",
        "http://10.232.196.179:5504",
    ],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(kiosk_router)
app.include_router(documents_router) 
app.include_router(print_jobs_router)
app.include_router(billing_router)
app.include_router(payment_router)
app.include_router(print_queue_router)
app.include_router(inventory_pricing_router)
app.include_router(customer_sessions_router)
app.include_router(customer_uploads_router)
app.include_router(customer_print_jobs_router)
app.include_router(customer_payments_router)
app.include_router(admin_dashboard_router)
app.include_router(admin_management_router)
app.include_router(kiosk_display_router)


@app.get("/")
async def root():
    return {
        "service": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment,
        "status": "running",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "service": settings.app_name,
        "version": settings.app_version,
    }





