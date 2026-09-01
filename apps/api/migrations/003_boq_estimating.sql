-- STEP 32: BOQ revisions and estimate items.
CREATE TABLE IF NOT EXISTS boq_revisions (
  id varchar(36) PRIMARY KEY,
  project_id varchar(36) NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
  budget_id varchar(36) REFERENCES budgets(id) ON DELETE SET NULL,
  revision_no integer NOT NULL,
  name varchar(255) NOT NULL,
  status varchar(32) NOT NULL DEFAULT 'DRAFT',
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now(),
  CONSTRAINT boq_revision_no_ck CHECK (revision_no > 0),
  CONSTRAINT boq_revision_status_ck CHECK (status IN ('DRAFT','APPROVED','ARCHIVED')),
  CONSTRAINT boq_revision_project_no_uq UNIQUE (project_id, revision_no)
);
CREATE INDEX IF NOT EXISTS idx_boq_revisions_project ON boq_revisions(project_id, revision_no DESC);

CREATE TABLE IF NOT EXISTS boq_items (
  id varchar(36) PRIMARY KEY,
  revision_id varchar(36) NOT NULL REFERENCES boq_revisions(id) ON DELETE CASCADE,
  item_code varchar(64) NOT NULL,
  description varchar(1000) NOT NULL,
  unit varchar(32) NOT NULL,
  quantity numeric(18,4) NOT NULL,
  unit_rate numeric(18,2) NOT NULL,
  total numeric(18,2) NOT NULL,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now(),
  CONSTRAINT boq_item_quantity_ck CHECK (quantity > 0),
  CONSTRAINT boq_item_rate_ck CHECK (unit_rate >= 0),
  CONSTRAINT boq_item_total_ck CHECK (total >= 0)
);
CREATE INDEX IF NOT EXISTS idx_boq_items_revision ON boq_items(revision_id);
CREATE INDEX IF NOT EXISTS idx_boq_items_code ON boq_items(revision_id, item_code);
