-- BuildCost Pro authentication schema (PostgreSQL)
CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TABLE IF NOT EXISTS users (
  id varchar(36) PRIMARY KEY,
  email varchar(320) NOT NULL UNIQUE,
  password_hash varchar(255) NOT NULL,
  role varchar(50) NOT NULL DEFAULT 'user',
  is_active boolean NOT NULL DEFAULT true,
  email_verified_at timestamptz NULL,
  failed_login_count integer NOT NULL DEFAULT 0,
  locked_until timestamptz NULL,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS auth_sessions (
  id varchar(36) PRIMARY KEY,
  user_id varchar(36) NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  refresh_token_hash varchar(128) NOT NULL UNIQUE,
  user_agent varchar(512),
  ip_address varchar(64),
  expires_at timestamptz NOT NULL,
  revoked_at timestamptz,
  created_at timestamptz NOT NULL DEFAULT now(),
  last_seen_at timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_auth_sessions_user ON auth_sessions(user_id);

CREATE TABLE IF NOT EXISTS auth_one_time_tokens (
  id varchar(36) PRIMARY KEY,
  user_id varchar(36) NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  purpose varchar(32) NOT NULL,
  token_hash varchar(128) NOT NULL UNIQUE,
  expires_at timestamptz NOT NULL,
  consumed_at timestamptz,
  created_at timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_auth_tokens_user_purpose ON auth_one_time_tokens(user_id, purpose);

CREATE TABLE IF NOT EXISTS auth_audit_logs (
  id varchar(36) PRIMARY KEY,
  user_id varchar(36) REFERENCES users(id) ON DELETE SET NULL,
  event varchar(80) NOT NULL,
  ip_address varchar(64),
  user_agent varchar(512),
  metadata_json text NOT NULL DEFAULT '{}',
  created_at timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_auth_audit_event_created ON auth_audit_logs(event, created_at);
CREATE INDEX IF NOT EXISTS idx_auth_audit_user_created ON auth_audit_logs(user_id, created_at);
