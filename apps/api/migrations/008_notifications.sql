-- STEP 38: in-app notifications, preferences and event rules.
CREATE TABLE IF NOT EXISTS notifications (
  id varchar(36) PRIMARY KEY,
  user_id varchar(36) NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  project_id varchar(36) REFERENCES projects(id) ON DELETE CASCADE,
  notification_type varchar(32) NOT NULL,
  title varchar(200) NOT NULL,
  message text NOT NULL,
  severity varchar(16) NOT NULL DEFAULT 'INFO',
  read_at timestamptz,
  created_at timestamptz NOT NULL DEFAULT now(),
  CONSTRAINT notification_severity_ck CHECK (severity IN ('INFO','SUCCESS','WARNING','ERROR'))
);
CREATE INDEX IF NOT EXISTS idx_notifications_user_created ON notifications(user_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_notifications_user_unread ON notifications(user_id, read_at) WHERE read_at IS NULL;

CREATE TABLE IF NOT EXISTS notification_preferences (
  id varchar(36) PRIMARY KEY,
  user_id varchar(36) NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
  in_app_enabled boolean NOT NULL DEFAULT true,
  threshold_alerts_enabled boolean NOT NULL DEFAULT true,
  approval_alerts_enabled boolean NOT NULL DEFAULT true,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS notification_rules (
  id varchar(36) PRIMARY KEY,
  user_id varchar(36) NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  project_id varchar(36) NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
  rule_type varchar(32) NOT NULL,
  threshold_percent integer,
  enabled boolean NOT NULL DEFAULT true,
  created_at timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_notification_rules_project ON notification_rules(project_id, enabled);
