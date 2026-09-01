from datetime import datetime
from pydantic import BaseModel, Field, field_validator

STATUSES = {"DRAFT", "IN_REVIEW", "APPROVED", "REJECTED", "ARCHIVED"}


class DocumentCreate(BaseModel):
    document_no: str = Field(min_length=1, max_length=64)
    title: str = Field(min_length=1, max_length=200)
    document_type: str = Field(min_length=1, max_length=64)


class DocumentResponse(BaseModel):
    id: str
    project_id: str
    document_no: str
    title: str
    document_type: str
    status: str
    current_version: int
    created_at: datetime
    updated_at: datetime
    model_config = {"from_attributes": True}


class DocumentVersionCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    content_hash: str | None = Field(default=None, max_length=128)
    notes: str | None = Field(default=None, max_length=500)


class DocumentVersionResponse(BaseModel):
    id: str
    document_id: str
    version_no: int
    title: str
    content_hash: str | None
    notes: str | None
    created_at: datetime
    model_config = {"from_attributes": True}


class AttachmentCreate(BaseModel):
    version_no: int = Field(gt=0)
    file_name: str = Field(min_length=1, max_length=255)
    storage_ref: str = Field(min_length=1, max_length=500)
    content_type: str | None = Field(default=None, max_length=120)
    size_bytes: int | None = Field(default=None, ge=0)


class AttachmentResponse(BaseModel):
    id: str
    document_id: str
    version_no: int
    file_name: str
    storage_ref: str
    content_type: str | None
    size_bytes: int | None
    created_at: datetime
    model_config = {"from_attributes": True}


class StatusTransition(BaseModel):
    to_status: str
    comment: str | None = Field(default=None, max_length=500)

    @field_validator("to_status")
    @classmethod
    def valid_status(cls, value: str) -> str:
        if value not in STATUSES:
            raise ValueError("invalid document status")
        return value


class ApprovalCreate(BaseModel):
    decision: str
    comment: str | None = Field(default=None, max_length=500)

    @field_validator("decision")
    @classmethod
    def valid_decision(cls, value: str) -> str:
        if value not in {"APPROVED", "REJECTED"}:
            raise ValueError("invalid approval decision")
        return value


class ApprovalResponse(BaseModel):
    id: str
    document_id: str
    version_no: int
    approver_user_id: str
    decision: str
    comment: str | None
    decided_at: datetime
    model_config = {"from_attributes": True}


class AuditResponse(BaseModel):
    id: str
    document_id: str
    version_no: int | None
    actor_user_id: str | None
    action: str
    from_status: str | None
    to_status: str | None
    detail: str | None
    created_at: datetime
    model_config = {"from_attributes": True}
