from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .auth_models import User
from .auth_router import current_user, db_session
from .notification_schemas import NotificationResponse, NotificationPreferenceResponse, NotificationPreferenceUpdate
from .notification_service import list_notifications, mark_read, get_or_create_preferences, update_preferences

router = APIRouter(prefix="/api/v1/notifications", tags=["notifications"])


@router.get("", response_model=list[NotificationResponse])
def notifications(unread_only: bool = False, user: User = Depends(current_user), db: Session = Depends(db_session)):
    return list_notifications(db, user.id, unread_only)


@router.post("/{notification_id}/read", response_model=NotificationResponse)
def notification_read(notification_id: str, user: User = Depends(current_user), db: Session = Depends(db_session)):
    item = mark_read(db, notification_id, user.id)
    if not item:
        raise HTTPException(status_code=404, detail="notification not found")
    return item


@router.get("/preferences", response_model=NotificationPreferenceResponse)
def preferences(user: User = Depends(current_user), db: Session = Depends(db_session)):
    return get_or_create_preferences(db, user.id)


@router.put("/preferences", response_model=NotificationPreferenceResponse)
def preferences_update(body: NotificationPreferenceUpdate, user: User = Depends(current_user), db: Session = Depends(db_session)):
    return update_preferences(db, user.id, body.model_dump())
