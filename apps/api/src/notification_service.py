from datetime import datetime, timezone
from sqlalchemy import select
from sqlalchemy.orm import Session
from .notification_models import Notification, NotificationPreference


def list_notifications(db: Session, user_id: str, unread_only: bool = False):
    stmt = select(Notification).where(Notification.user_id == user_id).order_by(Notification.created_at.desc())
    if unread_only:
        stmt = stmt.where(Notification.read_at.is_(None))
    return db.scalars(stmt).all()


def mark_read(db: Session, notification_id: str, user_id: str):
    notification = db.scalar(select(Notification).where(Notification.id == notification_id, Notification.user_id == user_id))
    if not notification:
        return None
    notification.read_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(notification)
    return notification


def create_notification(db: Session, payload: dict):
    pref = db.scalar(select(NotificationPreference).where(NotificationPreference.user_id == payload["user_id"]))
    if pref is None:
        pref = NotificationPreference(user_id=payload["user_id"])
        db.add(pref)
        db.flush()
    if not pref.in_app_enabled:
        db.rollback()
        return None
    notification = Notification(**payload)
    db.add(notification)
    db.commit()
    db.refresh(notification)
    return notification


def get_or_create_preferences(db: Session, user_id: str):
    pref = db.scalar(select(NotificationPreference).where(NotificationPreference.user_id == user_id))
    if pref is None:
        pref = NotificationPreference(user_id=user_id)
        db.add(pref)
        db.commit()
        db.refresh(pref)
    return pref


def update_preferences(db: Session, user_id: str, values: dict):
    pref = get_or_create_preferences(db, user_id)
    for key, value in values.items():
        setattr(pref, key, value)
    db.commit()
    db.refresh(pref)
    return pref
