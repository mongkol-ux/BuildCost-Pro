-- STEP 39: indexes supporting global/project search and permission-scoped lookups.
CREATE INDEX IF NOT EXISTS idx_projects_owner_code_name ON projects(owner_user_id, code, name);
CREATE INDEX IF NOT EXISTS idx_budgets_project_name ON budgets(project_id, name);
CREATE INDEX IF NOT EXISTS idx_costs_project_category ON costs(project_id, category);
CREATE INDEX IF NOT EXISTS idx_boq_revisions_project ON boq_revisions(project_id);
CREATE INDEX IF NOT EXISTS idx_boq_items_revision_code ON boq_items(revision_id, item_code);
CREATE INDEX IF NOT EXISTS idx_documents_project_title ON documents(project_id, title);
CREATE INDEX IF NOT EXISTS idx_procurement_requests_project_no ON procurement_requests(project_id, request_no);
CREATE INDEX IF NOT EXISTS idx_procurement_quotations_request_no ON procurement_quotations(request_id, quotation_no);
CREATE INDEX IF NOT EXISTS idx_purchase_orders_request_no ON purchase_orders(request_id, po_no);
CREATE INDEX IF NOT EXISTS idx_resources_code_name ON resources(code, name);
CREATE INDEX IF NOT EXISTS idx_suppliers_code_name ON suppliers(code, name);
