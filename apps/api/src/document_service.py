from datetime import datetime, timezone
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from .core_models import Project
from .document_models import Document, DocumentVersion, DocumentAttachment, DocumentApproval, DocumentAuditLog

ALLOWED = {
    "DRAFT": {"IN_REVIEW", "ARCHIVED"},
    "IN_REVIEW": {"APPROVED", "REJECTED", "DRAFT"},
    "APPROVED": {"ARCHIVED", "DRAFT"},
    "REJECTED": {"DRAFT", "IN_REVIEW", "ARCHIVED"},
    "ARCHIVED": set(),
}


def _project(db: Session, project_id: str, user_id: str, role: str) -> Project:
    stmt = select(Project).where(Project.id == project_id)
    if role != "admin":
        stmt = stmt.where(Project.owner_user_id == user_id)
    value = db.scalar(stmt)
    if not value:
        raise HTTPException(status_code=404, detail="project not found")
    return value


def _doc(db: Session, project_id: str, document_id: str) -> Document:
    value = db.scalar(select(Document).where(Document.id == document_id, Document.project_id == project_id))
    if not value:
        raise HTTPException(status_code=404, detail="document not found")
    return value


def _audit(db: Session, doc: Document, user_id: str, action: str, detail: str | None = None, from_status: str | None = None, to_status: str | None = None):
    db.add(DocumentAuditLog(document_id=doc.id, version_no=doc.current_version, actor_user_id=user_id, action=action, detail=detail, from_status=from_status, to_status=to_status))


def create_document(db: Session, project_id: str, user_id: str, role: str, data: dict) -> Document:
    _project(db, project_id, user_id, role)
    exists = db.scalar(select(Document).where(Document.project_id == project_id, Document.document_no == data["document_no"]))
    if exists:
        raise HTTPException(status_code=409, detail="document number already exists")
    doc = Document(project_id=project_id, created_by=user_id, updated_at=datetime.now(timezone.utc), **data)
    db.add(doc)
    db.flush()
    db.add(DocumentVersion(document_id=doc.id, version_no=1, title=doc.title, created_by=user_id))
    _audit(db, doc, user_id, "CREATED")
    db.commit(); db.refresh(doc)
    return doc


def list_documents(db: Session, project_id: str, user_id: str, role: str) -> list[Document]:
    _project(db, project_id, user_id, role)
    return list(db.scalars(select(Document).where(Document.project_id == project_id).order_by(Document.updated_at.desc())).all())


def create_version(db: Session, project_id: str, document_id: str, user_id: str, role: str, data: dict) -> DocumentVersion:
    _project(db, project_id, user_id, role); doc = _doc(db, project_id, document_id)
    if doc.status == "ARCHIVED":
        raise HTTPException(status_code=409, detail="archived document cannot be versioned")
    doc.current_version += 1; doc.title = data["title"]; doc.updated_at = datetime.now(timezone.utc)
    version = DocumentVersion(document_id=doc.id, version_no=doc.current_version, created_by=user_id, **data)
    db.add(version); _audit(db, doc, user_id, "VERSION_CREATED", f"version={doc.current_version}")
    db.commit(); db.refresh(version); return version


def list_versions(db: Session, project_id: str, document_id: str, user_id: str, role: str) -> list[DocumentVersion]:
    _project(db, project_id, user_id, role); doc = _doc(db, project_id, document_id)
    return list(db.scalars(select(DocumentVersion).where(DocumentVersion.document_id == doc.id).order_by(DocumentVersion.version_no.desc())).all())


def add_attachment(db: Session, project_id: str, document_id: str, user_id: str, role: str, data: dict) -> DocumentAttachment:
    _project(db, project_id, user_id, role); doc = _doc(db, project_id, document_id)
    if data["version_no"] > doc.current_version:
        raise HTTPException(status_code=422, detail="attachment version does not exist")
    item = DocumentAttachment(document_id=doc.id, created_by=user_id, **data)
    db.add(item); _audit(db, doc, user_id, "ATTACHMENT_ADDED", data["file_name"])
    db.commit(); db.refresh(item); return item


def list_attachments(db: Session, project_id: str, document_id: str, user_id: str, role: str) -> list[DocumentAttachment]:
    _project(db, project_id, user_id, role); doc = _doc(db, project_id, document_id)
    return list(db.scalars(select(DocumentAttachment).where(DocumentAttachment.document_id == doc.id).order_by(DocumentAttachment.created_at.desc())).all())


def transition(db: Session, project_id: str, document_id: str, user_id: str, role: str, to_status: str, comment: str | None) -> Document:
    _project(db, project_id, user_id, role); doc = _doc(db, project_id, document_id)
    if to_status not in ALLOWED[doc.status]:
        raise HTTPException(status_code=409, detail=f"invalid transition from {doc.status} to {to_status}")
    old = doc.status; doc.status = to_status; doc.updated_at = datetime.now(timezone.utc)
    _audit(db, doc, user_id, "STATUS_CHANGED", comment, old, to_status)
    db.commit(); db.refresh(doc); return doc


def approve(db: Session, project_id: str, document_id: str, user_id: str, role: str, decision: str, comment: str | None) -> DocumentApproval:
    _project(db, project_id, user_id, role); doc = _doc(db, project_id, document_id)
    if doc.status != "IN_REVIEW":
        raise HTTPException(status_code=409, detail="document must be in review before approval")
    approval = DocumentApproval(document_id=doc.id, version_no=doc.current_version, approver_user_id=user_id, decision=decision, comment=comment)
    db.add(approval)
    old = doc.status; doc.status = decision; doc.updated_at = datetime.now(timezone.utc)
    _audit(db, doc, user_id, "APPROVAL_RECORDED", comment, old, decision)
    db.commit(); db.refresh(approval); return approval


def list_approvals(db: Session, project_id: str, document_id: str, user_id: str, role: str) -> list[DocumentApproval]:
    _project(db, project_id, user_id, role); doc = _doc(db, project_id, document_id)
    return list(db.scalars(select(DocumentApproval).where(DocumentApproval.document_id == doc.id).order_by(DocumentApproval.decided_at.desc())).all())


def list_audit(db: Session, project_id: str, document_id: str, user_id: str, role: str) -> list[DocumentAuditLog]:
    _project(db, project_id, user_id, role); doc = _doc(db, project_id, document_id)
    return list(db.scalars(select(DocumentAuditLog).where(DocumentAuditLog.document_id == doc.id).order_by(DocumentAuditLog.created_at.desc())).all())
