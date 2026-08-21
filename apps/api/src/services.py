from sqlalchemy import select
from sqlalchemy.orm import Session
from .errors import conflict, not_found
from .models import Budget, Cost, Project, Transaction, User


class ProjectService:
    @staticmethod
    def create(db: Session, owner: User, data):
        if db.scalar(select(Project).where(Project.code == data.code)):
            raise conflict("Project code already exists")
        project = Project(**data.model_dump(), owner_id=owner.id)
        db.add(project); db.commit(); db.refresh(project)
        return project

    @staticmethod
    def get(db: Session, project_id: str):
        project = db.get(Project, project_id)
        if project is None:
            raise not_found("Project")
        return project

    @staticmethod
    def list_for_user(db: Session, user: User):
        stmt = select(Project).order_by(Project.created_at.desc())
        if user.role == "user":
            stmt = stmt.where(Project.owner_id == user.id)
        return list(db.scalars(stmt))


class MoneyService:
    model = None

    @classmethod
    def create(cls, db: Session, data):
        project = db.get(Project, data.project_id)
        if project is None:
            raise not_found("Project")
        obj = cls.model(**data.model_dump())
        db.add(obj); db.commit(); db.refresh(obj)
        return obj

    @classmethod
    def list(cls, db: Session, project_id: str):
        if db.get(Project, project_id) is None:
            raise not_found("Project")
        return list(db.scalars(select(cls.model).where(cls.model.project_id == project_id).order_by(cls.model.created_at.desc())))


class CostService(MoneyService):
    model = Cost


class BudgetService(MoneyService):
    model = Budget


class TransactionService(MoneyService):
    model = Transaction
