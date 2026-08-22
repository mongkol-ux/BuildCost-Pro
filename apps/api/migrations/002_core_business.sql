-- BuildCost Pro core business schema: projects, budgets, costs and transactions.
CREATE TABLE IF NOT EXISTS projects (
  id varchar(36) PRIMARY KEY,
  owner_user_id varchar(36) NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
  code varchar(64) NOT NULL UNIQUE,
  name varchar(255) NOT NULL,
  description text,
  status varchar(32) NOT NULL DEFAULT 'DRAFT',
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now(),
  CONSTRAINT projects_status_ck CHECK (status IN ('DRAFT','ACTIVE','COMPLETED','ARCHIVED'))
);
CREATE INDEX IF NOT EXISTS idx_projects_owner_status ON projects(owner_user_id, status);

CREATE TABLE IF NOT EXISTS budgets (
  id varchar(36) PRIMARY KEY,
  project_id varchar(36) NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
  name varchar(255) NOT NULL,
  amount numeric(18,2) NOT NULL,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now(),
  CONSTRAINT budgets_amount_ck CHECK (amount >= 0)
);
CREATE INDEX IF NOT EXISTS idx_budgets_project ON budgets(project_id);

CREATE TABLE IF NOT EXISTS costs (
  id varchar(36) PRIMARY KEY,
  project_id varchar(36) NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
  category varchar(80) NOT NULL,
  description text,
  quantity numeric(18,4) NOT NULL,
  unit_cost numeric(18,2) NOT NULL,
  total numeric(18,2) NOT NULL,
  occurred_at timestamptz NOT NULL DEFAULT now(),
  created_at timestamptz NOT NULL DEFAULT now(),
  CONSTRAINT costs_quantity_ck CHECK (quantity > 0),
  CONSTRAINT costs_unit_cost_ck CHECK (unit_cost >= 0),
  CONSTRAINT costs_total_ck CHECK (total >= 0)
);
CREATE INDEX IF NOT EXISTS idx_costs_project_occurred ON costs(project_id, occurred_at);

CREATE TABLE IF NOT EXISTS transactions (
  id varchar(36) PRIMARY KEY,
  project_id varchar(36) NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
  type varchar(32) NOT NULL,
  reference varchar(120),
  description text,
  amount numeric(18,2) NOT NULL,
  occurred_at timestamptz NOT NULL DEFAULT now(),
  created_at timestamptz NOT NULL DEFAULT now(),
  CONSTRAINT transactions_type_ck CHECK (type IN ('INCOME','EXPENSE','ADJUSTMENT')),
  CONSTRAINT transactions_amount_ck CHECK (amount >= 0)
);
CREATE INDEX IF NOT EXISTS idx_transactions_project_occurred ON transactions(project_id, occurred_at);
