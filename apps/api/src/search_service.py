from sqlalchemy import select
from sqlalchemy.orm import Session

from .core_models import Project, Budget, Cost, BOQItem, BOQRevision
from .document_models import Document
from .resource_models import Resource, Supplier
from .procurement_models import ProcurementRequest, ProcurementQuotation, PurchaseOrder


def _matches(query: str, *values) -> bool:
    needle = query.casefold()
    return any(value is not None and needle in str(value).casefold() for value in values)


def _add(rows, query, entity_type, item_id, title, subtitle=None, project_id=None, fields=()):
    if not _matches(query, *fields):
        return
    score = 100 if str(title).casefold().startswith(query.casefold()) else 80
    rows.append((score, {"id": item_id, "entity_type": entity_type, "title": str(title), "subtitle": subtitle, "project_id": project_id, "score": score}))


def search(db: Session, user_id: str, query: str, project_id: str | None, page: int, page_size: int):
    query = query.strip()
    if not query:
        return 0, []

    projects = db.scalars(select(Project).where(Project.owner_user_id == user_id)).all()
    owned_ids = {p.id for p in projects}
    if project_id and project_id not in owned_ids:
        return 0, []

    def allowed(pid):
        return pid in owned_ids and (project_id is None or pid == project_id)

    rows = []
    for p in projects:
        if project_id is None or p.id == project_id:
            _add(rows, query, "project", p.id, p.name, p.code, p.id, (p.name, p.code, p.description))

    for item in db.scalars(select(Budget)).all():
        if allowed(item.project_id):
            _add(rows, query, "budget", item.id, item.name, None, item.project_id, (item.name,))

    for item in db.scalars(select(Cost)).all():
        if allowed(item.project_id):
            _add(rows, query, "cost", item.id, item.description or item.category, item.category, item.project_id, (item.category, item.description))

    for item in db.scalars(select(BOQItem)).all():
        revision = db.get(BOQRevision, item.revision_id)
        pid = revision.project_id if revision else None
        if allowed(pid):
            _add(rows, query, "boq_item", item.id, item.description, item.item_code, pid, (item.item_code, item.description, item.unit))

    for item in db.scalars(select(Document)).all():
        if allowed(item.project_id):
            _add(rows, query, "document", item.id, item.title, item.document_no, item.project_id, (item.document_no, item.title, item.document_type, item.status))

    requests = db.scalars(select(ProcurementRequest)).all()
    request_project = {r.id: r.project_id for r in requests if allowed(r.project_id)}
    for item in requests:
        if allowed(item.project_id):
            _add(rows, query, "procurement_request", item.id, item.request_no, item.status, item.project_id, (item.request_no, item.status))

    for item in db.scalars(select(ProcurementQuotation)).all():
        pid = request_project.get(item.request_id)
        if pid:
            _add(rows, query, "quotation", item.id, item.quotation_no, item.status, pid, (item.quotation_no, item.status))

    for item in db.scalars(select(PurchaseOrder)).all():
        pid = request_project.get(item.request_id)
        if pid:
            _add(rows, query, "purchase_order", item.id, item.po_no, item.status, pid, (item.po_no, item.status))

    # Resource and supplier masters are intentionally global, non-project-owned records.
    for item in db.scalars(select(Resource)).all():
        _add(rows, query, "resource", item.id, item.name, item.code, None, (item.code, item.name, item.unit))
    for item in db.scalars(select(Supplier)).all():
        _add(rows, query, "supplier", item.id, item.name, item.code, None, (item.code, item.name, item.contact_name, item.email))

    rows.sort(key=lambda x: (-x[0], x[1]["entity_type"], x[1]["title"].casefold()))
    total = len(rows)
    start = (page - 1) * page_size
    return total, [item for _, item in rows[start:start + page_size]]
