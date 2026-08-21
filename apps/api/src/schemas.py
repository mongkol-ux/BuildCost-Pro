from decimal import Decimal
from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class APIModel(BaseModel):
    model_config = ConfigDict(from_attributes=True, str_strip_whitespace=True)


class UserRegister(APIModel):
    email: EmailStr
    full_name: str = Field(min_length=2, max_length=200)
    password: str = Field(min_length=12, max_length=128)


class UserRead(APIModel):
    id: str
    email: EmailStr
    full_name: str
    role: str
    is_active: bool


class Token(APIModel):
    access_token: str
    token_type: str = "bearer"


class ProjectCreate(APIModel):
    name: str = Field(min_length=2, max_length=200)
    code: str = Field(min_length=2, max_length=50, pattern=r"^[A-Za-z0-9_-]+$")
    description: str | None = Field(default=None, max_length=5000)


class ProjectRead(ProjectCreate):
    id: str
    owner_id: str


class MoneyCreate(APIModel):
    project_id: str
    description: str = Field(min_length=2, max_length=500)
    amount: Decimal = Field(gt=0, max_digits=14, decimal_places=2)

    @field_validator("project_id")
    @classmethod
    def validate_project_id(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("project_id is required")
        return value


class CostCreate(MoneyCreate):
    category: str = Field(min_length=2, max_length=100)


class BudgetCreate(MoneyCreate):
    name: str = Field(min_length=2, max_length=200)


class TransactionCreate(MoneyCreate):
    reference: str = Field(min_length=2, max_length=100)


class CostRead(CostCreate):
    id: str


class BudgetRead(BudgetCreate):
    id: str


class TransactionRead(TransactionCreate):
    id: str
