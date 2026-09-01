from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
import csv
import io
from .auth_models import User
from .auth_router import current_user, db_session
from .reporting_service import dashboard

router = APIRouter(prefix="/api/v1/reports", tags=["reporting"])


@router.get("/projects/{project_id}/dashboard")
def project_dashboard(project_id: str, user: User = Depends(current_user), db: Session = Depends(db_session)):
    return dashboard(db, project_id, user.id, user.role)


@router.get("/projects/{project_id}/export.csv")
def project_export(project_id: str, user: User = Depends(current_user), db: Session = Depends(db_session)):
    report = dashboard(db, project_id, user.id, user.role)
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["metric", "value"])
    for key, value in report.kpi.model_dump().items():
        writer.writerow([key, value])
    writer.writerow(["boq_total", report.boq_total])
    writer.writerow(["boq_items", report.boq_items])
    writer.writerow(["procurement_commitment", report.procurement_commitment])
    for row in report.cost_by_category:
        writer.writerow([f"cost_category:{row.category}", row.amount])
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=project-{project_id}-report.csv"},
    )
