-- STEP 33 / M3 Resources & Suppliers
CREATE TABLE IF NOT EXISTS resource_categories (
  id VARCHAR(36) PRIMARY KEY,
  name VARCHAR(120) NOT NULL UNIQUE,
  resource_type VARCHAR(32) NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  CONSTRAINT resource_categories_type_ck CHECK (resource_type IN ('MATERIAL','LABOR','EQUIPMENT'))
);

CREATE TABLE IF NOT EXISTS suppliers (
  id VARCHAR(36) PRIMARY KEY,
  code VARCHAR(64) NOT NULL UNIQUE,
  name VARCHAR(255) NOT NULL,
  contact_name VARCHAR(255),
  phone VARCHAR(80),
  email VARCHAR(255),
  active BOOLEAN NOT NULL DEFAULT TRUE,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS resources (
  id VARCHAR(36) PRIMARY KEY,
  code VARCHAR(64) NOT NULL UNIQUE,
  name VARCHAR(255) NOT NULL,
  resource_type VARCHAR(32) NOT NULL,
  category_id VARCHAR(36) REFERENCES resource_categories(id) ON DELETE SET NULL,
  unit VARCHAR(32) NOT NULL,
  supplier_id VARCHAR(36) REFERENCES suppliers(id) ON DELETE SET NULL,
  active BOOLEAN NOT NULL DEFAULT TRUE,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  CONSTRAINT resources_type_ck CHECK (resource_type IN ('MATERIAL','LABOR','EQUIPMENT'))
);

CREATE TABLE IF NOT EXISTS resource_rates (
  id VARCHAR(36) PRIMARY KEY,
  resource_id VARCHAR(36) NOT NULL REFERENCES resources(id) ON DELETE CASCADE,
  rate NUMERIC(18,2) NOT NULL,
  effective_from DATE NOT NULL,
  effective_to DATE,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  CONSTRAINT resource_rates_rate_ck CHECK (rate >= 0),
  CONSTRAINT resource_rates_dates_ck CHECK (effective_to IS NULL OR effective_to >= effective_from),
  UNIQUE(resource_id, effective_from)
);

CREATE INDEX IF NOT EXISTS ix_resources_type ON resources(resource_type);
CREATE INDEX IF NOT EXISTS ix_resources_supplier ON resources(supplier_id);
CREATE INDEX IF NOT EXISTS ix_resource_rates_resource_date ON resource_rates(resource_id, effective_from);
