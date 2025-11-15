from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime


class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    income_category: str = "medium"


class UserOut(BaseModel):
    id: int
    name: str
    email: EmailStr
    income_category: str
    karma_points: int

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class GroupCreate(BaseModel):
    name: str
    description: Optional[str] = None


class GroupOut(BaseModel):
    id: int
    name: str
    description: Optional[str] = None

    class Config:
        from_attributes = True


class ExpenseCreate(BaseModel):
    amount: float
    description: Optional[str] = None
    category_id: Optional[int] = None


class ExpenseShareOut(BaseModel):
    user_id: int
    amount: float
    is_settled: bool

    class Config:
        from_attributes = True


class ExpenseOut(BaseModel):
    id: int
    amount: float
    description: Optional[str]
    created_at: datetime
    shares: List[ExpenseShareOut]

    class Config:
        from_attributes = True
