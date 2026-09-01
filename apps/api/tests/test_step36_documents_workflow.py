from types import SimpleNamespace
import pytest
from fastapi import HTTPException
from pydantic import ValidationError
from src.document_schemas import AttachmentCreate, DocumentCreate, StatusTransition
from src.document_service import transition


def test_document_create_requires_metadata():
    item = DocumentCreate(document_no="DOC-001", title="Estimate", document_type="ESTIMATE")
    assert item.document_no == "DOC-001"


def test_attachment_rejects_negative_size():
    with pytest.raises(ValidationError):
        AttachmentCreate(version_no=1, file_name="estimate.pdf", storage_ref="s3://bucket/key", size_bytes=-1)


def test_status_transition_rejects_unknown_status():
    with pytest.raises(ValidationError):
        StatusTransition(to_status="UNKNOWN")


def test_document_workflow_allows_draft_to_review(monkeypatch):
    doc = SimpleNamespace(id="doc", project_id="project", status="DRAFT", current_version=1, updated_at=None)
    project = SimpleNamespace(id="project")
    class DB:
        def add(self, obj): pass
        def commit(self): pass
        def refresh(self, obj): pass
    monkeypatch.setattr("src.document_service._project", lambda *args: project)
    monkeypatch.setattr("src.document_service._doc", lambda *args: doc)
    result = transition(DB(), "project", "doc", "user", "admin", "IN_REVIEW", "submit")
    assert result.status == "IN_REVIEW"


def test_document_workflow_rejects_invalid_transition(monkeypatch):
    doc = SimpleNamespace(id="doc", project_id="project", status="ARCHIVED", current_version=1, updated_at=None)
    project = SimpleNamespace(id="project")
    class DB:
        def add(self, obj): pass
        def commit(self): pass
        def refresh(self, obj): pass
    monkeypatch.setattr("src.document_service._project", lambda *args: project)
    monkeypatch.setattr("src.document_service._doc", lambda *args: doc)
    with pytest.raises(HTTPException) as exc:
        transition(DB(), "project", "doc", "user", "admin", "DRAFT", None)
    assert exc.value.status_code == 409
