from sqlalchemy import (
    Column, Integer, String, ForeignKey, Float, Boolean, DateTime, Text
)
from sqlalchemy.orm import relationship
from datetime import datetime
from .db import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)

    # выбранная категория дохода (для автокоэффициента)
    income_category = Column(String, default="medium")  # low | medium | high

    karma_points = Column(Integer, default=0)

    memberships = relationship("GroupMember", back_populates="user")


class Group(Base):
    __tablename__ = "groups"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    owner_id = Column(Integer, ForeignKey("users.id"))

    members = relationship("GroupMember", back_populates="group")
    expenses = relationship("Expense", back_populates="group")


class GroupMember(Base):
    __tablename__ = "group_members"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    group_id = Column(Integer, ForeignKey("groups.id"))

    # коэффициент справедливости, задаётся системой
    fairness_coeff = Column(Float, default=1.0)

    user = relationship("User", back_populates="memberships")
    group = relationship("Group", back_populates="members")


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)


class Expense(Base):
    __tablename__ = "expenses"

    id = Column(Integer, primary_key=True, index=True)
    group_id = Column(Integer, ForeignKey("groups.id"))
    creator_id = Column(Integer, ForeignKey("users.id"))
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)

    amount = Column(Float, nullable=False)
    description = Column(String, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    group = relationship("Group", back_populates="expenses")
    shares = relationship("ExpenseShare", back_populates="expense")
    history = relationship("ExpenseHistory", back_populates="expense")


class ExpenseShare(Base):
    """
    Конкретная доля участника по расходу, уже рассчитанная с учётом коэффициента.
    """
    __tablename__ = "expense_shares"

    id = Column(Integer, primary_key=True, index=True)
    expense_id = Column(Integer, ForeignKey("expenses.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    amount = Column(Float, nullable=False)
    is_settled = Column(Boolean, default=False)

    expense = relationship("Expense", back_populates="shares")
    user = relationship("User")


class ExpenseHistory(Base):
    """
    История изменений по расходу — чтобы соответствовать ТЗ.
    """
    __tablename__ = "expense_history"

    id = Column(Integer, primary_key=True, index=True)
    expense_id = Column(Integer, ForeignKey("expenses.id"))
    changed_at = Column(DateTime, default=datetime.utcnow)
    change_desc = Column(Text)

    expense = relationship("Expense", back_populates="history")


class KarmaLog(Base):
    __tablename__ = "karma_log"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    points = Column(Integer, nullable=False)
    reason = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
