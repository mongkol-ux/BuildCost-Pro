"""BuildCost Pro API application and security boundary."""
import logging
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware
from .auth_router import router as auth_router
from .config import get_settings
from .core_router import router as core_router
from .database import bootstrap_database
from .resource_router import router as resource_router
from .procurement_router import router as procurement_router
from .accounting_router import router as accounting_router
from .document_router import router as document_router
from .reporting_router import router as reporting_router
from .notification_router import router as notification_router
from .search_router import router as search_router
from . import accounting_models  # noqa: F401 - register accounting ORM tables
from . import document_models  # noqa: F401 - register document ORM tables
from . import notification_models  # noqa: F401 - register notification ORM tables
from . import resource_models  # noqa: F401 - register resource ORM tables
from . import procurement_models  # noqa: F401 - register procurement ORM tables

settings = get_settings()
logger = logging.getLogger("buildcost_pro.security")
docs_url = None if settings.environment == "production" else "/docs"
redoc_url = None if settings.environment == "production" else "/redoc"


@asynccontextmanager
async def lifespan(_: FastAPI):
    bootstrap_database()
    yield


app = FastAPI(title=settings.app_name, version="1.0.0", docs_url=docs_url, redoc_url=redoc_url, lifespan=lifespan)
app.add_middleware(TrustedHostMiddleware, allowed_hosts=settings.get_allowed_hosts())
app.add_middleware(CORSMiddleware, allow_origins=settings.get_cors_origins(), allow_credentials=False, allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"], allow_headers=["Authorization", "Content-Type", "X-Requested-With"])

@app.middleware("http")
async def security_headers(request, call_next):
    request_id = request.headers.get("x-request-id") or str(uuid.uuid4())
    try:
        response = await call_next(request)
    except Exception:
        logger.exception("unhandled_request_error method=%s path=%s request_id=%s", request.method, request.url.path, request_id)
        raise
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    # The API is intentionally consumed cross-origin by the production Web app.
    response.headers["Cross-Origin-Resource-Policy"] = "cross-origin"
    response.headers["X-Permitted-Cross-Domain-Policies"] = "none"
    response.headers["Content-Security-Policy"] = "default-src 'none'; frame-ancestors 'none'"
    response.headers["Cache-Control"] = "no-store" if request.url.path.startswith("/auth") else "no-cache"
    forwarded_proto = request.headers.get("x-forwarded-proto", "").split(",", 1)[0].strip().lower()
    if settings.environment == "production" or forwarded_proto == "https":
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    if response.status_code >= 400 and request.url.path != "/health":
        logger.warning("security_http_event status=%s method=%s path=%s request_id=%s", response.status_code, request.method, request.url.path, request_id)
    return response

@app.get("/health", tags=["system"])
def health() -> dict[str, str]:
    return {"status": "ok", "service": "buildcost-pro-api", "version": "1.0.0"}

app.include_router(auth_router)
app.include_router(core_router)
app.include_router(resource_router)
app.include_router(procurement_router)
app.include_router(accounting_router)
app.include_router(document_router)
app.include_router(reporting_router)
app.include_router(notification_router)
app.include_router(search_router)
