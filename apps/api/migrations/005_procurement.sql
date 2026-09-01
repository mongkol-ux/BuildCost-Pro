-- STEP 34: procurement request, quotation, purchase order and receiving lifecycle.
CREATE TABLE IF NOT EXISTS procurement_requests (
  id varchar(36) PRIMARY KEY,
  project_id varchar(36) NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
  request_no varchar(64) NOT NULL,
  status varchar(32) NOT NULL DEFAULT 'DRAFT',
  needed_by date,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now(),
  CONSTRAINT procurement_request_status_ck CHECK (status IN ('DRAFT','SUBMITTED','APPROVED','ORDERED','RECEIVED','CANCELLED')),
  CONSTRAINT procurement_request_project_no_uq UNIQUE (project_id, request_no)
);
CREATE INDEX IF NOT EXISTS idx_procurement_requests_project ON procurement_requests(project_id, created_at DESC);

CREATE TABLE IF NOT EXISTS procurement_request_items (
  id varchar(36) PRIMARY KEY,
  request_id varchar(36) NOT NULL REFERENCES procurement_requests(id) ON DELETE CASCADE,
  resource_id varchar(36) NOT NULL REFERENCES resources(id) ON DELETE RESTRICT,
  quantity numeric(18,4) NOT NULL,
  unit_rate numeric(18,2) NOT NULL,
  total numeric(18,2) NOT NULL,
  CONSTRAINT procurement_request_item_qty_ck CHECK (quantity > 0),
  CONSTRAINT procurement_request_item_rate_ck CHECK (unit_rate >= 0),
  CONSTRAINT procurement_request_item_total_ck CHECK (total >= 0)
);
CREATE INDEX IF NOT EXISTS idx_procurement_request_items_request ON procurement_request_items(request_id);

CREATE TABLE IF NOT EXISTS procurement_quotations (
  id varchar(36) PRIMARY KEY,
  request_id varchar(36) NOT NULL REFERENCES procurement_requests(id) ON DELETE CASCADE,
  supplier_id varchar(36) NOT NULL REFERENCES suppliers(id) ON DELETE RESTRICT,
  quotation_no varchar(64) NOT NULL,
  amount numeric(18,2) NOT NULL,
  status varchar(32) NOT NULL DEFAULT 'RECEIVED',
  quoted_at date NOT NULL,
  CONSTRAINT procurement_quotation_amount_ck CHECK (amount >= 0),
  CONSTRAINT procurement_quotation_status_ck CHECK (status IN ('RECEIVED','SELECTED','REJECTED')),
  CONSTRAINT procurement_quotation_request_no_uq UNIQUE (request_id, quotation_no)
);
CREATE INDEX IF NOT EXISTS idx_procurement_quotations_request ON procurement_quotations(request_id, amount);

CREATE TABLE IF NOT EXISTS purchase_orders (
  id varchar(36) PRIMARY KEY,
  request_id varchar(36) NOT NULL REFERENCES procurement_requests(id) ON DELETE CASCADE,
  supplier_id varchar(36) NOT NULL REFERENCES suppliers(id) ON DELETE RESTRICT,
  quotation_id varchar(36) REFERENCES procurement_quotations(id) ON DELETE SET NULL,
  po_no varchar(64) NOT NULL,
  status varchar(32) NOT NULL DEFAULT 'DRAFT',
  total numeric(18,2) NOT NULL,
  ordered_at date,
  created_at timestamptz NOT NULL DEFAULT now(),
  CONSTRAINT purchase_order_status_ck CHECK (status IN ('DRAFT','ISSUED','PARTIALLY_RECEIVED','RECEIVED','CANCELLED')),
  CONSTRAINT purchase_order_total_ck CHECK (total >= 0),
  CONSTRAINT purchase_order_no_uq UNIQUE (po_no)
);
CREATE INDEX IF NOT EXISTS idx_purchase_orders_request ON purchase_orders(request_id, created_at DESC);

CREATE TABLE IF NOT EXISTS purchase_order_items (
  id varchar(36) PRIMARY KEY,
  purchase_order_id varchar(36) NOT NULL REFERENCES purchase_orders(id) ON DELETE CASCADE,
  resource_id varchar(36) NOT NULL REFERENCES resources(id) ON DELETE RESTRICT,
  quantity numeric(18,4) NOT NULL,
  unit_rate numeric(18,2) NOT NULL,
  total numeric(18,2) NOT NULL,
  received_quantity numeric(18,4) NOT NULL DEFAULT 0,
  CONSTRAINT purchase_order_item_qty_ck CHECK (quantity > 0),
  CONSTRAINT purchase_order_item_rate_ck CHECK (unit_rate >= 0),
  CONSTRAINT purchase_order_item_total_ck CHECK (total >= 0),
  CONSTRAINT purchase_order_item_received_ck CHECK (received_quantity >= 0 AND received_quantity <= quantity)
);
CREATE INDEX IF NOT EXISTS idx_purchase_order_items_po ON purchase_order_items(purchase_order_id);
