"""HTTP authentication endpoints."""
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, Header, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt import InvalidTokenError
from sqlalchemy import select
from sqlalchemy.orm import Session
from .auth_models import AuthSession, User
from .auth_schemas import LoginRequest, OneTimeTokenRequest, PasswordResetEmailRequest, PasswordResetRequest, RefreshRequest, RegisterRequest, SessionResponse, TokenResponse
from .auth_security import decode_access_token
from .auth_service import login, register, request_password_reset, reset_password, revoke_all_sessions, revoke_session, rotate_refresh, verify_email
from .database import SessionLocal

router = APIRouter(prefix="/auth", tags=["authentication"])
bearer = HTTPBearer(auto_error=False)


def db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def client_meta(request: Request, forwarded_for: str | None, user_agent: str | None):
    ip = forwarded_for.split(",")[0].strip() if forwarded_for else (request.client.host if request.client else None)
    return ip, user_agent or request.headers.get("user-agent")


def current_user(credentials: HTTPAuthorizationCredentials | None = Depends(bearer), db: Session = Depends(db_session)) -> User:
    if not credentials:
        raise HTTPException(status_code=401, detail="authentication required")
    try:
        payload = decode_access_token(credentials.credentials)
    except InvalidTokenError:
        raise HTTPException(status_code=401, detail="invalid access token")
    session = db.scalar(select(AuthSession).where(AuthSession.id == payload["sid"], AuthSession.user_id == payload["sub"]))
    if not session or session.revoked_at or session.expires_at <= datetime.now(timezone.utc):
        raise HTTPException(status_code=401, detail="session is not active")
    user = db.get(User, payload["sub"])
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="user is not active")
    session.last_seen_at = datetime.now(timezone.utc)
    db.commit()
    return user


@router.post("/register", status_code=201)
def register_endpoint(body: RegisterRequest, request: Request, x_forwarded_for: str | None = Header(None), user_agent: str | None = Header(None), db: Session = Depends(db_session)):
    ip, ua = client_meta(request, x_forwarded_for, user_agent)
    try:
        user = register(db, body.email, body.password, ip, ua)
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc))
    return {"id": user.id, "email": user.email, "verification_required": True}


@router.post("/login", response_model=TokenResponse)
def login_endpoint(body: LoginRequest, request: Request, x_forwarded_for: str | None = Header(None), user_agent: str | None = Header(None), db: Session = Depends(db_session)):
    ip, ua = client_meta(request, x_forwarded_for, user_agent)
    try:
        access, refresh, expires_in = login(db, body.email, body.password, ip, ua)
    except PermissionError as exc:
        raise HTTPException(status_code=423, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=401, detail=str(exc))
    return TokenResponse(access_token=access, refresh_token=refresh, expires_in=expires_in)


@router.post("/refresh", response_model=TokenResponse)
def refresh_endpoint(body: RefreshRequest, request: Request, x_forwarded_for: str | None = Header(None), user_agent: str | None = Header(None), db: Session = Depends(db_session)):
    ip, ua = client_meta(request, x_forwarded_for, user_agent)
    try:
        access, refresh, expires_in = rotate_refresh(db, body.refresh_token, ip, ua)
    except PermissionError as exc:
        raise HTTPException(status_code=401, detail=str(exc))
    return TokenResponse(access_token=access, refresh_token=refresh, expires_in=expires_in)


@router.post("/verify-email")
def verify_email_endpoint(body: OneTimeTokenRequest, db: Session = Depends(db_session)):
    try:
        verify_email(db, body.token)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return {"verified": True}


@router.post("/password-reset/request")
def password_reset_request_endpoint(body: PasswordResetEmailRequest, db: Session = Depends(db_session)):
    request_password_reset(db, body.email)
    return {"accepted": True}


@router.post("/password-reset/confirm")
def password_reset_confirm_endpoint(body: PasswordResetRequest, db: Session = Depends(db_session)):
    try:
        reset_password(db, body.token, body.new_password)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return {"reset": True}


@router.get("/sessions", response_model=list[SessionResponse])
def list_sessions(user: User = Depends(current_user), db: Session = Depends(db_session)):
    rows = db.scalars(select(AuthSession).where(AuthSession.user_id == user.id, AuthSession.revoked_at.is_(None))).all()
    return [SessionResponse(id=s.id, user_agent=s.user_agent, ip_address=s.ip_address, created_at=s.created_at.isoformat(), last_seen_at=s.last_seen_at.isoformat(), expires_at=s.expires_at.isoformat()) for s in rows]


@router.delete("/sessions/{session_id}", status_code=204)
def revoke_session_endpoint(session_id: str, user: User = Depends(current_user), db: Session = Depends(db_session)):
    revoke_session(db, session_id, user.id)


@router.post("/sessions/revoke-all", status_code=204)
def revoke_all_sessions_endpoint(user: User = Depends(current_user), db: Session = Depends(db_session)):
    revoke_all_sessions(db, user.id)
