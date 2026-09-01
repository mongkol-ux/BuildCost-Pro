from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from .auth_models import User
from .auth_router import current_user, db_session
from .search_schemas import SearchResponse
from .search_service import search

router = APIRouter(prefix="/api/v1/search", tags=["search"])


@router.get("", response_model=SearchResponse)
def global_search(
    q: str = Query(..., min_length=1, max_length=120),
    project_id: str | None = Query(None),
    page: int = Query(1, ge=1, le=10000),
    page_size: int = Query(20, ge=1, le=100),
    user: User = Depends(current_user),
    db: Session = Depends(db_session),
):
    total, results = search(db, user.id, q, project_id, page, page_size)
    return SearchResponse(query=q.strip(), page=page, page_size=page_size, total=total, results=results)
