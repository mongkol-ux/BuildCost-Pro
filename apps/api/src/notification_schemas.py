from datetime import datetime
from pydantic import BaseModel, Field


class NotificationResponse(BaseModel):
    id: str
    project_id: str | None
    notification_type: str
    title: str
    message: str
    severity: str
    read_at: datetime | None
    created_at: datetime


class NotificationPreferenceResponse(BaseModel):
    in_app_enabled: bool
    threshold_alerts_enabled: bool
    approval_alerts_enabled: bool


class NotificationPreferenceUpdate(BaseModel):
    in_app_enabled: bool = True
    threshold_alerts_enabled: bool = True
    approval_alerts_enabled: bool = True


class NotificationCreate(BaseModel):
    user_id: str
    project_id: str | None = None
    notification_type: str = Field(min_length=1, max_length=32)
    title: str = Field(min_length=1, max_length=200)
    message: str = Field(min_length=1)
    severity: str = Field(default="INFO", min_length=1, max_length=16)
