-- STEP 35 / M5 Accounting & Financial Controls
ALTER TABLE transactions ADD COLUMN IF NOT EXISTS financial_period_id varchar(36) REFERENCES financial_periods(id) ON DELETE RESTRICT;
ALTER TABLE transactions ADD COLUMN IF NOT EXISTS category varchar(80);
ALTER TABLE transactions ADD COLUMN IF NOT EXISTS tax_amount numeric(18,2) NOT NULL DEFAULT 0;
ALTER TABLE transactions ADD COLUMN IF NOT EXISTS retention_amount numeric(18,2) NOT NULL DEFAULT 0;
ALTER TABLE transactions ADD COLUMN IF NOT EXISTS payment_status varchar(32) NOT NULL DEFAULT 'UNPAID';

CREATE TABLE IF NOT EXISTS financial_periods (
  id varchar(36) PRIMARY KEY,
  project_id varchar(36) NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
  period_code varchar(32) NOT NULL,
  start_date date NOT NULL,
  end_date date NOT NULL,
  status varchar(16) NOT NULL DEFAULT 'OPEN',
  closed_at timestamptz,
  created_at timestamptz NOT NULL DEFAULT now(),
  CONSTRAINT financial_period_dates_ck CHECK (end_date >= start_date),
  CONSTRAINT financial_period_status_ck CHECK (status IN ('OPEN','CLOSED')),
  CONSTRAINT financial_period_project_code_uq UNIQUE (project_id, period_code)
);

CREATE TABLE IF NOT EXISTS payments (
  id varchar(36) PRIMARY KEY,
  project_id varchar(36) NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
  transaction_id varchar(36) REFERENCES transactions(id) ON DELETE SET NULL,
  amount numeric(18,2) NOT NULL,
  payment_date date NOT NULL,
  status varchar(16) NOT NULL DEFAULT 'PAID',
  reference varchar(120),
  created_at timestamptz NOT NULL DEFAULT now(),
  CONSTRAINT payment_amount_ck CHECK (amount > 0),
  CONSTRAINT payment_status_ck CHECK (status IN ('PAID','VOID'))
);

CREATE TABLE IF NOT EXISTS retentions (
  id varchar(36) PRIMARY KEY,
  project_id varchar(36) NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
  transaction_id varchar(36) REFERENCES transactions(id) ON DELETE SET NULL,
  amount numeric(18,2) NOT NULL,
  released_amount numeric(18,2) NOT NULL DEFAULT 0,
  status varchar(24) NOT NULL DEFAULT 'HELD',
  release_date date,
  created_at timestamptz NOT NULL DEFAULT now(),
  CONSTRAINT retention_amount_ck CHECK (amount > 0),
  CONSTRAINT retention_released_ck CHECK (released_amount >= 0 AND released_amount <= amount),
  CONSTRAINT retention_status_ck CHECK (status IN ('HELD','PARTIALLY_RELEASED','RELEASED'))
);

CREATE TABLE IF NOT EXISTS reconciliations (
  id varchar(36) PRIMARY KEY,
  project_id varchar(36) NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
  financial_period_id varchar(36) NOT NULL REFERENCES financial_periods(id) ON DELETE RESTRICT,
  expected_total numeric(18,2) NOT NULL,
  actual_total numeric(18,2) NOT NULL,
  difference numeric(18,2) NOT NULL,
  status varchar(16) NOT NULL,
  reconciled_at timestamptz NOT NULL DEFAULT now(),
  CONSTRAINT reconciliation_expected_ck CHECK (expected_total >= 0),
  CONSTRAINT reconciliation_actual_ck CHECK (actual_total >= 0),
  CONSTRAINT reconciliation_status_ck CHECK (status IN ('MATCHED','MISMATCH'))
);

CREATE INDEX IF NOT EXISTS idx_financial_periods_project_dates ON financial_periods(project_id, start_date, end_date);
CREATE INDEX IF NOT EXISTS idx_transactions_period ON transactions(financial_period_id, occurred_at);
CREATE INDEX IF NOT EXISTS idx_payments_project_date ON payments(project_id, payment_date);
CREATE INDEX IF NOT EXISTS idx_retentions_project_status ON retentions(project_id, status);
CREATE INDEX IF NOT EXISTS idx_reconciliations_period ON reconciliations(financial_period_id, reconciled_at DESC);
