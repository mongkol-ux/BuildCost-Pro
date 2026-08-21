from typing import Annotated
from fastapi import APIRouter, Depends, FastAPI, Form, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from .auth import create_access_token, get_current_user, hash_password, require_roles, verify_password
from .config import assert_secure_configuration, settings
from .db import get_db
from .models import User, UserRole
from .schemas import BudgetCreate, BudgetRead, CostCreate, CostRead, ProjectCreate, ProjectRead, Token, TransactionCreate, TransactionRead, UserRead, UserRegister
from .services import BudgetService, CostService, ProjectService, TransactionService

assert_secure_configuration()
router = APIRouter(prefix="/api/v1")


@router.get("/health", tags=["system"])
def health():
    return {"status": "ok", "service": "buildcost-pro-api", "version": settings.app_version}


auth = APIRouter(prefix="/auth", tags=["auth"])


@auth.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def register(data: UserRegister, db: Session = Depends(get_db)):
    if db.scalar(select(User).where(User.email == data.email.lower())):
        return JSONResponse(status_code=409, content={"code": "EMAIL_EXISTS", "message": "Email already registered"})
    user = User(email=data.email.lower(), full_name=data.full_name, password_hash=hash_password(data.password), role=UserRole.USER)
    db.add(user)
    try:
        db.commit(); db.refresh(user)
    except IntegrityError:
        db.rollback()
        return JSONResponse(status_code=409, content={"code": "EMAIL_EXISTS", "message": "Email already registered"})
    return user


@auth.post("/login", response_model=Token)
def login(username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    user = db.scalar(select(User).where(User.email == username.lower()))
    if user is None or not verify_password(password, user.password_hash) or not user.is_active:
        return JSONResponse(status_code=401, content={"code": "INVALID_CREDENTIALS", "message": "Invalid email or password"}, headers={"WWW-Authenticate": "Bearer"})
    return Token(access_token=create_access_token(user))


@auth.get("/me", response_model=UserRead)
def me(user: User = Depends(get_current_user)):
    return user

router.include_router(auth)

projects = APIRouter(prefix="/projects", tags=["projects"])


@projects.post("", response_model=ProjectRead, status_code=201)
def create_project(data: ProjectCreate, db: Session = Depends(get_db), user: User = Depends(require_roles(UserRole.ADMIN, UserRole.MANAGER))):
    return ProjectService.create(db, user, data)


@projects.get("", response_model=list[ProjectRead])
def list_projects(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return ProjectService.list_for_user(db, user)


@projects.get("/{project_id}", response_model=ProjectRead)
def get_project(project_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    project = ProjectService.get(db, project_id)
    if user.role == UserRole.USER and project.owner_id != user.id:
        from fastapi import HTTPException
        raise HTTPException(status_code=403, detail={"code": "FORBIDDEN", "message": "Insufficient permissions"})
    return project

router.include_router(projects)


def money_router(path: str, service, create_schema, read_schema):
    r = APIRouter(prefix=path, tags=[path.strip("/")])

    @r.post("", response_model=read_schema, status_code=201)
    def create(data: create_schema, db: Session = Depends(get_db), user: User = Depends(require_roles(UserRole.ADMIN, UserRole.MANAGER))):
        project = ProjectService.get(db, data.project_id)
        if user.role == UserRole.USER and project.owner_id != user.id:
            from fastapi import HTTPException
            raise HTTPException(status_code=403, detail={"code": "FORBIDDEN", "message": "Insufficient permissions"})
        return service.create(db, data)

    @r.get("", response_model=list[read_schema])
    def list_items(project_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
        project = ProjectService.get(db, project_id)
        if user.role == UserRole.USER and project.owner_id != user.id:
            from fastapi import HTTPException
            raise HTTPException(status_code=403, detail={"code": "FORBIDDEN", "message": "Insufficient permissions"})
        return service.list(db, project_id)
    return r

router.include_router(money_router("/costs", CostService, CostCreate, CostRead))
router.include_router(money_router("/budgets", BudgetService, BudgetCreate, BudgetRead))
router.include_router(money_router("/transactions", TransactionService, TransactionCreate, TransactionRead))


def create_app() -> FastAPI:
    app = FastAPI(title=settings.app_name, version=settings.app_version)

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        return JSONResponse(status_code=422, content={"code": "VALIDATION_ERROR", "message": "Request validation failed", "details": exc.errors()})

    @app.exception_handler(IntegrityError)
    async def integrity_exception_handler(request: Request, exc: IntegrityError):
        return JSONResponse(status_code=409, content={"code": "INTEGRITY_ERROR", "message": "Request conflicts with existing data"})

    @app.get("/", tags=["system"])
    def root():
        return {"service": settings.app_name, "version": settings.app_version}

    app.include_router(router)
    return app


app = create_app()
