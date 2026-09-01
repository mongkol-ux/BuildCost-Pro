from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from .auth_models import User
from .auth_router import current_user, db_session
from .document_schemas import DocumentCreate, DocumentResponse, DocumentVersionCreate, DocumentVersionResponse, AttachmentCreate, AttachmentResponse, StatusTransition, ApprovalCreate, ApprovalResponse, AuditResponse
from .document_service import create_document, list_documents, create_version, list_versions, add_attachment, list_attachments, transition, approve, list_approvals, list_audit

router = APIRouter(prefix="/api/v1", tags=["documents"])


@router.get("/projects/{project_id}/documents", response_model=list[DocumentResponse])
def documents(project_id: str, user: User = Depends(current_user), db: Session = Depends(db_session)):
    return list_documents(db, project_id, user.id, user.role)


@router.post("/projects/{project_id}/documents", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
def document_create(project_id: str, body: DocumentCreate, user: User = Depends(current_user), db: Session = Depends(db_session)):
    return create_document(db, project_id, user.id, user.role, body.model_dump())


@router.get("/projects/{project_id}/documents/{document_id}/versions", response_model=list[DocumentVersionResponse])
def versions(project_id: str, document_id: str, user: User = Depends(current_user), db: Session = Depends(db_session)):
    return list_versions(db, project_id, document_id, user.id, user.role)


@router.post("/projects/{project_id}/documents/{document_id}/versions", response_model=DocumentVersionResponse, status_code=status.HTTP_201_CREATED)
def version_create(project_id: str, document_id: str, body: DocumentVersionCreate, user: User = Depends(current_user), db: Session = Depends(db_session)):
    return create_version(db, project_id, document_id, user.id, user.role, body.model_dump())


@router.get("/projects/{project_id}/documents/{document_id}/attachments", response_model=list[AttachmentResponse])
def attachments(project_id: str, document_id: str, user: User = Depends(current_user), db: Session = Depends(db_session)):
    return list_attachments(db, project_id, document_id, user.id, user.role)


@router.post("/projects/{project_id}/documents/{document_id}/attachments", response_model=AttachmentResponse, status_code=status.HTTP_201_CREATED)
def attachment_create(project_id: str, document_id: str, body: AttachmentCreate, user: User = Depends(current_user), db: Session = Depends(db_session)):
    return add_attachment(db, project_id, document_id, user.id, user.role, body.model_dump())


@router.post("/projects/{project_id}/documents/{document_id}/transition", response_model=DocumentResponse)
def document_transition(project_id: str, document_id: str, body: StatusTransition, user: User = Depends(current_user), db: Session = Depends(db_session)):
    return transition(db, project_id, document_id, user.id, user.role, body.to_status, body.comment)


@router.post("/projects/{project_id}/documents/{document_id}/approval", response_model=ApprovalResponse, status_code=status.HTTP_201_CREATED)
def document_approval(project_id: str, document_id: str, body: ApprovalCreate, user: User = Depends(current_user), db: Session = Depends(db_session)):
    return approve(db, project_id, document_id, user.id, user.role, body.decision, body.comment)


@router.get("/projects/{project_id}/documents/{document_id}/approvals", response_model=list[ApprovalResponse])
def approvals(project_id: str, document_id: str, user: User = Depends(current_user), db: Session = Depends(db_session)):
    return list_approvals(db, project_id, document_id, user.id, user.role)


@router.get("/projects/{project_id}/documents/{document_id}/audit", response_model=list[AuditResponse])
def audit(project_id: str, document_id: str, user: User = Depends(current_user), db: Session = Depends(db_session)):
    return list_audit(db, project_id, document_id, user.id, user.role)
