from src.main import app
from src.notification_models import Notification, NotificationPreference, NotificationRule
from src.notification_schemas import NotificationCreate, NotificationPreferenceUpdate


def test_step38_routes_registered():
    paths = set(app.openapi()["paths"])
    assert "/api/v1/notifications" in paths
    assert "/api/v1/notifications/{notification_id}/read" in paths
    assert "/api/v1/notifications/preferences" in paths


def test_step38_models_and_tables_registered():
    assert Notification.__tablename__ == "notifications"
    assert NotificationPreference.__tablename__ == "notification_preferences"
    assert NotificationRule.__tablename__ == "notification_rules"
    assert "severity" in Notification.__table__.c
    assert "read_at" in Notification.__table__.c


def test_step38_request_contract_defaults():
    body = NotificationCreate(user_id="u1", notification_type="THRESHOLD", title="Budget alert", message="Threshold reached")
    assert body.severity == "INFO"
    prefs = NotificationPreferenceUpdate()
    assert prefs.in_app_enabled is True
    assert prefs.threshold_alerts_enabled is True
    assert prefs.approval_alerts_enabled is True
