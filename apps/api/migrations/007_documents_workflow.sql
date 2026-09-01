-- STEP 36: document metadata/versioning, attachment references, approvals and audit trail.
CREATE TABLE IF NOT EXISTS documents (
  id varchar(36) PRIMARY KEY,
  project_id varchar(36) NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
  document_no varchar(64) NOT NULL,
  title varchar(200) NOT NULL,
  document_type varchar(64) NOT NULL,
  status varchar(32) NOT NULL DEFAULT 'DRAFT',
  current_version integer NOT NULL DEFAULT 1,
  created_by varchar(36),
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now(),
  CONSTRAINT document_status_ck CHECK (status IN ('DRAFT','IN_REVIEW','APPROVED','REJECTED','ARCHIVED')),
  CONSTRAINT document_version_ck CHECK (current_version > 0),
  CONSTRAINT document_project_no_uq UNIQUE (project_id, document_no)
);
CREATE INDEX IF NOT EXISTS idx_documents_project_status ON documents(project_id, status, updated_at DESC);

CREATE TABLE IF NOT EXISTS document_versions (
  id varchar(36) PRIMARY KEY,
  document_id varchar(36) NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
  version_no integer NOT NULL,
  title varchar(200) NOT NULL,
  content_hash varchar(128),
  notes varchar(500),
  created_by varchar(36),
  created_at timestamptz NOT NULL DEFAULT now(),
  CONSTRAINT document_version_no_ck CHECK (version_no > 0),
  CONSTRAINT document_version_uq UNIQUE (document_id, version_no)
);
CREATE INDEX IF NOT EXISTS idx_document_versions_document ON document_versions(document_id, version_no DESC);

CREATE TABLE IF NOT EXISTS document_attachments (
  id varchar(36) PRIMARY KEY,
  document_id varchar(36) NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
  version_no integer NOT NULL,
  file_name varchar(255) NOT NULL,
  storage_ref varchar(500) NOT NULL,
  content_type varchar(120),
  size_bytes bigint,
  created_by varchar(36),
  created_at timestamptz NOT NULL DEFAULT now(),
  CONSTRAINT attachment_version_ck CHECK (version_no > 0),
  CONSTRAINT attachment_size_ck CHECK (size_bytes IS NULL OR size_bytes >= 0)
);
CREATE INDEX IF NOT EXISTS idx_document_attachments_document ON document_attachments(document_id, version_no DESC);

CREATE TABLE IF NOT EXISTS document_approvals (
  id varchar(36) PRIMARY KEY,
  document_id varchar(36) NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
  version_no integer NOT NULL,
  approver_user_id varchar(36) NOT NULL,
  decision varchar(24) NOT NULL,
  comment varchar(500),
  decided_at timestamptz NOT NULL DEFAULT now(),
  CONSTRAINT document_approval_version_ck CHECK (version_no > 0),
  CONSTRAINT document_approval_decision_ck CHECK (decision IN ('APPROVED','REJECTED'))
);
CREATE INDEX IF NOT EXISTS idx_document_approvals_document ON document_approvals(document_id, decided_at DESC);

CREATE TABLE IF NOT EXISTS document_audit_log (
  id varchar(36) PRIMARY KEY,
  document_id varchar(36) NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
  version_no integer,
  actor_user_id varchar(36),
  action varchar(64) NOT NULL,
  from_status varchar(32),
  to_status varchar(32),
  detail varchar(1000),
  created_at timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_document_audit_document ON document_audit_log(document_id, created_at DESC);
