"""API contracts for authentication."""
from pydantic import BaseModel, EmailStr, Field, field_validator


def validate_strong_password(value: str) -> str:
    if not any(c.islower() for c in value) or not any(c.isupper() for c in value) or not any(c.isdigit() for c in value):
        raise ValueError("password must include upper, lower and numeric characters")
    return value


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=12, max_length=128)
    _strong = field_validator("password")(validate_strong_password)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class RefreshRequest(BaseModel):
    refresh_token: str = Field(min_length=32)


class OneTimeTokenRequest(BaseModel):
    token: str = Field(min_length=32)


class PasswordResetRequest(BaseModel):
    token: str = Field(min_length=32)
    new_password: str = Field(min_length=12, max_length=128)
    _strong = field_validator("new_password")(validate_strong_password)


class PasswordResetEmailRequest(BaseModel):
    email: EmailStr


class SessionResponse(BaseModel):
    id: str
    user_agent: str | None
    ip_address: str | None
    created_at: str
    last_seen_at: str
    expires_at: str
