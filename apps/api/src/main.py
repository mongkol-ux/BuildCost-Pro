"""BuildCost Pro API application and security boundary."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware
from .auth_router import router as auth_router
from .config import get_settings
from .core_router import router as core_router
from .resource_router import router as resource_router

settings = get_settings()
docs_url = None if settings.environment == "production" else "/docs"
redoc_url = None if settings.environment == "production" else "/redoc"
app = FastAPI(title=settings.app_name, version="1.0.0", docs_url=docs_url, redoc_url=redoc_url)
app.add_middleware(TrustedHostMiddleware, allowed_hosts=settings.get_allowed_hosts())
app.add_middleware(CORSMiddleware, allow_origins=[o.strip() for o in settings.cors_origins.split(",") if o.strip()], allow_credentials=False, allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"], allow_headers=["Authorization", "Content-Type", "X-Requested-With"])

@app.middleware("http")
async def security_headers(request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    response.headers["Cache-Control"] = "no-store" if request.url.path.startswith("/auth") else "no-cache"
    forwarded_proto = request.headers.get("x-forwarded-proto", "").split(",", 1)[0].strip().lower()
    if settings.environment == "production" or forwarded_proto == "https":
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return response

@app.get("/health", tags=["system"])
def health() -> dict[str, str]:
    return {"status": "ok", "service": "buildcost-pro-api", "version": "1.0.0"}

app.include_router(auth_router)
app.include_router(core_router)
app.include_router(resource_router)
