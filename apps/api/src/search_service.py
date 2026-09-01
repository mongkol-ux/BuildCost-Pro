from sqlalchemy import or_, select, func
from sqlalchemy.orm import Session

from .core_models import Project, Budget, Cost, BOQItem
from .resource_models import Resource, Supplier
from .procurement_models import ProcurementRequest, ProcurementQuotation, PurchaseOrder


def _like(term: str, *columns):
    return or_(*[column.ilike(term) for column in columns])


def search(db: Session, user_id: str, query: str, project_id: str | None, page: int, page_size: int):
    q = query.strip()
    if not q:
        return 0, []
    term = f"%{q}%"
    rows = []

    # Project-owned entities are always constrained through the owning project.
    project_rows = db.scalars(select(Project).where(Project.owner_user_id == user_id)).all()
    owned_project_ids = {p.id for p in project_rows}
    if project_id and project_id not in owned_project_ids:
        return 0, []

    def allowed(pid):
        return pid in owned_project_ids and (project_id is None or pid == project_id)

    for p in project_rows:
        if project_id is None or p.id == project_id:
            score = 100 if q.lower() in p.name.lower() else 90 if q.lower() in p.code.lower() else 70
            if _match(score, p.name, p.code, p.description):
                rows.append((score, {"id": p.id, "entity_type": "project", "title": p.name, "subtitle": p.code, "project_id": p.id, "score": score}))

    for model, entity, title_fields, subtitle_field, pid_field in [
        (Budget, "budget", ("name",), None, "project_id"),
        (Cost, "cost", ("category", "description"), "category", "project_id"),
        (BOQItem, "boq_item", ("item_code", "description"), "item_code", None),
        (ProcurementRequest, "procurement_request", ("request_no", "status"), "request_no", "project_id"),
    ]:
        stmt = select(model)
        if pid_field:
            stmt = stmt.where(getattr(model, pid_field).in_(owned_project_ids))
            if project_id:
                stmt = stmt.where(getattr(model, pid_field) == project_id)
        elif model is BOQItem:
            stmt = stmt.join(__import__('buildcost', fromlist=['x']) if False else Project, False) if False else stmt
        for item in db.scalars(stmt).all():
            pid = getattr(item, pid_field) if pid_field else None
            if model is BOQItem:
                # BOQ ownership is resolved from its revision/project relationship via a correlated lookup.
                rev = db.get(__import__('apps.api.src.core_models', fromlist=['BOQRevision']).BOQRevision, item.revision_id)
                pid = rev.project_id if rev else None
                if not allowed(pid):
                    continue
            if not _match(1, *(getattr(item, f, None) for f in title_fields)):
                continue
            title = next((str(getattr(item, f)) for f in title_fields if getattr(item, f, None)), entity)
            subtitle = str(getattr(item, subtitle_field)) if subtitle_field and getattr(item, subtitle_field, None) else None
            rows.append((1, {"id": item.id, "entity_type": entity, "title": title, "subtitle": subtitle, "project_id": pid, "score": 1}))

    for model, entity, fields in [
        (Resource, "resource", ("code", "name", "unit")),
        (Supplier, "supplier", ("code", "name", "contact_name", "email")),
    ]:
        for item in db.scalars(select(model)).all():
            if not _match(1, *(getattr(item, f, None) for f in fields)):
                continue
            title = str(getattr(item, "name", getattr(item, "code", entity)))
            subtitle = str(getattr(item, "code", "")) or None
            rows.append((1, {"id": item.id, "entity_type": entity, "title": title, "subtitle": subtitle, "project_id": None, "score": 1}))

    # Procurement records beyond requests are project-owned through the request.
    reqs = {r.id: r.project_id for r in db.scalars(select(ProcurementRequest).where(ProcurementRequest.project_id.in_(owned_project_ids))).all()}
    for model, entity, fields in [
        (ProcurementQuotation, "quotation", ("quotation_no", "status")),
        (PurchaseOrder, "purchase_order", ("po_no", "status")),
    ]:
        for item in db.scalars(select(model)).all():
            pid = reqs.get(item.request_id)
            if not allowed(pid) or not _match(1, *(getattr(item, f, None) for f in fields)):
                continue
            title = str(getattr(item, fields[0]))
            rows.append((1, {"id": item.id, "entity_type": entity, "title": title, "subtitle": str(getattr(item, fields[1], "")), "project_id": pid, "score": 1}))

    rows.sort(key=lambda x: (-x[0], x[1]["entity_type"], x[1]["title"].lower()))
    total = len(rows)
    start = (page - 1) * page_size
    return total, [item for _, item in rows[start:start + page_size]]


def _match(_score, *values):
    # Case-insensitive application-level fallback keeps this service SQLite-test friendly.
    return any(v is not None and str(value).lower() in str(v).lower() for v in values if (value := _current_query()))

_CURRENT = ""
def _current_query():
    return _CURRENT
