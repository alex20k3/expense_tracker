from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

class UserBase(BaseModel):
    name: str
    email: EmailStr
    income_category: str = "medium"  # "low" / "medium" / "high"

class UserCreate(UserBase):
    password: str


class UserOut(UserBase):
    id: int
    karma_points: int

    class Config:
        from_attributes = True  # вместо orm_mode в pydantic v2



class Token(BaseModel):
    access_token: str
    token_type: str


class GroupBase(BaseModel):
    name: str
    description: Optional[str] = None


class GroupCreate(GroupBase):
    pass


class GroupOut(GroupBase):
    id: int
    owner_id: int

    class Config:
        orm_mode = True


class ExpenseCreate(BaseModel):
    amount: float
    description: Optional[str] = None
    category_id: Optional[int] = None


class ExpenseShareOut(BaseModel):
    user_id: int
    user_name: str
    amount: float          # полный долг
    paid_amount: float     # уже оплачено
    is_settled: bool

    class Config:
        from_attributes = True



class ExpenseOut(BaseModel):
    id: int
    group_id: int
    creator_id: int
    amount: float
    description: Optional[str] = None
    shares: List[ExpenseShareOut] = []

    class Config:
        from_attributes = True


class PaymentIn(BaseModel):
    amount: float