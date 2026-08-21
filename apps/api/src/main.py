"""BuildCost Pro API with Authentication Security Hardening V2."""
import os, secrets
from datetime import timedelta
from fastapi import FastAPI, HTTPException, Request, Response, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr, Field
from .security import (store, User, hash_password, verify_password, new_session, rotate_refresh,
    current_identity, require_permission, now, timedelta, RESET_TTL_SECONDS, VERIFY_TTL_SECONDS,
    LOCKOUT_SECONDS, MAX_FAILED_LOGINS)

app = FastAPI(title="BuildCost Pro API", version="1.0.0", docs_url="/docs", redoc_url="/redoc")

origins = [x.strip() for x in os.getenv("BCP_CORS_ORIGINS", "http://localhost:3000").split(",") if x.strip()]
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_credentials=True,
                   allow_methods=["GET","POST","DELETE","OPTIONS"], allow_headers=["Authorization","Content-Type","X-Request-ID"])

@app.middleware("http")
async def security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    response.headers["Content-Security-Policy"] = "default-src 'none'; frame-ancestors 'none'"
    if request.url.scheme == "https": response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return response

class RegisterIn(BaseModel):
    email: EmailStr
    password: str = Field(min_length=12, max_length=128)
class LoginIn(BaseModel):
    email: EmailStr
    password: str
class RefreshIn(BaseModel): refresh_token: str = Field(min_length=32)
class CodeIn(BaseModel): token: str = Field(min_length=20)
class ResetIn(BaseModel):
    token: str = Field(min_length=20)
    password: str = Field(min_length=12, max_length=128)


def _token(kind: str, user_id: str, ttl: int) -> str:
    raw = secrets.token_urlsafe(48)
    store.one_time_tokens[raw] = (kind, user_id, now() + timedelta(seconds=ttl))
    return raw

@app.get("/health", tags=["system"])
def health():
    return {"status":"ok","service":"buildcost-pro-api","version":"1.0.0"}

@app.post("/auth/register", status_code=201, tags=["auth"])
def register(payload: RegisterIn, request: Request):
    key = f"register:{request.client.host if request.client else 'unknown'}"; store.rate_limit(key, 10, 3600)
    email = payload.email.lower()
    if any(u.email == email for u in store.users.values()): raise HTTPException(409, "Account already exists")
    uid = secrets.token_urlsafe(18); user = User(uid, email, hash_password(payload.password)); store.users[uid] = user
    token = _token("verify", uid, VERIFY_TTL_SECONDS); store.audit_event("account.registered", uid, request)
    return {"user_id":uid,"email":email,"email_verified":False,"verification_token":token}

@app.post("/auth/login", tags=["auth"])
def login(payload: LoginIn, request: Request):
    ip = request.client.host if request.client else "unknown"; store.rate_limit(f"login-ip:{ip}", 20, 300)
    email = payload.email.lower(); user = next((u for u in store.users.values() if u.email == email), None)
    if not user:
        raise HTTPException(401, "Invalid credentials")
    if user.locked_until and user.locked_until > now(): raise HTTPException(423, "Account temporarily locked")
    if not verify_password(payload.password, user.password_hash):
        user.failed_logins += 1; store.audit_event("auth.login_failed", user.id, request)
        if user.failed_logins >= MAX_FAILED_LOGINS:
            user.locked_until = now() + timedelta(seconds=LOCKOUT_SECONDS); user.failed_logins = 0
            store.audit_event("auth.account_locked", user.id, request)
        raise HTTPException(401, "Invalid credentials")
    user.failed_logins = 0; user.locked_until = None
    session, refresh, access = new_session(user, request); store.audit_event("auth.login_success", user.id, request, session_id=session.id)
    return {"access_token":access,"token_type":"bearer","expires_in":900,"refresh_token":refresh,"session_id":session.id}

@app.post("/auth/refresh", tags=["auth"])
def refresh(payload: RefreshIn, request: Request):
    store.rate_limit(f"refresh:{request.client.host if request.client else 'unknown'}", 30, 300)
    user, session, raw, access = rotate_refresh(payload.refresh_token, request)
    store.audit_event("auth.refresh_rotated", user.id, request, session_id=session.id)
    return {"access_token":access,"token_type":"bearer","expires_in":900,"refresh_token":raw,"session_id":session.id}

@app.post("/auth/logout", tags=["auth"])
def logout(identity=Depends(current_identity)):
    user, session = identity; session.revoked_at = now(); return {"status":"ok"}

@app.post("/auth/logout-all", tags=["auth"])
def logout_all(identity=Depends(current_identity)):
    user, _ = identity
    for s in store.sessions.values():
        if s.user_id == user.id and not s.revoked_at: s.revoked_at = now()
    return {"status":"ok"}

@app.get("/auth/sessions", tags=["auth"])
def sessions(identity=Depends(require_permission("session:read"))):
    user, current = identity
    return [{"id":s.id,"created_at":s.created_at,"expires_at":s.expires_at,"revoked":bool(s.revoked_at),"current":s.id==current.id,"ip":s.ip,"user_agent":s.user_agent} for s in store.sessions.values() if s.user_id == user.id]

@app.delete("/auth/sessions/{session_id}", tags=["auth"])
def revoke_session(session_id: str, identity=Depends(require_permission("session:revoke"))):
    user, _ = identity; session = store.sessions.get(session_id)
    if not session or session.user_id != user.id: raise HTTPException(404, "Session not found")
    session.revoked_at = now(); return {"status":"ok"}

@app.post("/auth/verify-email/request", tags=["auth"])
def request_verification(request: Request, identity=Depends(current_identity)):
    user, _ = identity; store.rate_limit(f"verify:{user.id}", 5, 3600); token = _token("verify", user.id, VERIFY_TTL_SECONDS)
    return {"verification_token":token}

@app.post("/auth/verify-email/confirm", tags=["auth"])
def confirm_verification(payload: CodeIn, request: Request):
    item = store.one_time_tokens.pop(payload.token, None)
    if not item or item[0] != "verify" or item[2] <= now(): raise HTTPException(400, "Invalid verification token")
    user = store.users.get(item[1]);
    if not user: raise HTTPException(400, "Invalid verification token")
    user.email_verified = True; store.audit_event("account.email_verified", user.id, request); return {"email_verified":True}

@app.post("/auth/password-reset/request", tags=["auth"])
def request_reset(payload: dict, request: Request):
    email = str(payload.get("email", "")).lower(); store.rate_limit(f"reset:{request.client.host if request.client else 'unknown'}", 5, 3600)
    user = next((u for u in store.users.values() if u.email == email), None)
    if user: return {"status":"accepted","reset_token":_token("reset", user.id, RESET_TTL_SECONDS)}
    return {"status":"accepted"}

@app.post("/auth/password-reset/confirm", tags=["auth"])
def confirm_reset(payload: ResetIn, request: Request):
    item = store.one_time_tokens.pop(payload.token, None)
    if not item or item[0] != "reset" or item[2] <= now(): raise HTTPException(400, "Invalid reset token")
    user = store.users.get(item[1]);
    if not user: raise HTTPException(400, "Invalid reset token")
    user.password_hash = hash_password(payload.password); user.failed_logins = 0; user.locked_until = None
    for s in store.sessions.values():
        if s.user_id == user.id and not s.revoked_at: s.revoked_at = now()
    store.audit_event("account.password_reset", user.id, request); return {"status":"ok"}

@app.get("/auth/me", tags=["auth"])
def me(identity=Depends(require_permission("profile:read"))):
    user, _ = identity; return {"id":user.id,"email":user.email,"role":user.role,"email_verified":user.email_verified}

@app.get("/admin/audit-log", tags=["security"])
def audit_log(identity=Depends(require_permission("audit:read"))):
    return store.audit[-500:]
