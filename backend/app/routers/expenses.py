from typing import List

from fastapi import APIRouter, Depends, HTTPException
from fastapi import Response
from sqlalchemy.orm import Session

from .. import schemas, models, utils
from ..deps import get_db, get_current_user

router = APIRouter(prefix="/expenses", tags=["expenses"])


@router.post("/group/{group_id}", response_model=schemas.ExpenseOut)
def create_expense(
    group_id: int,
    expense_in: schemas.ExpenseCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    group = db.query(models.Group).filter_by(id=group_id).first()
    if not group:
        raise HTTPException(404, "Group not found")

    member = (
        db.query(models.GroupMember)
        .filter_by(group_id=group_id, user_id=current_user.id)
        .first()
    )
    if not member:
        raise HTTPException(403, "You are not a member of this group")

    # due_date: либо из запроса, либо дефолт (если в модели дефолт есть - можно не передавать)
    expense = models.Expense(
        group_id=group_id,
        creator_id=current_user.id,
        amount=expense_in.amount,
        description=expense_in.description,
        category_id=getattr(expense_in, "category_id", None),
        due_date=getattr(expense_in, "due_date", None),  # если нет поля в схеме — просто игнор
    )

    db.add(expense)
    db.commit()
    db.refresh(expense)

    # создаём доли
    members = db.query(models.GroupMember).filter_by(group_id=group_id).all()
    total_coeff = sum(m.fairness_coeff for m in members) or 1

    for m in members:
        user_amount = round(expense.amount * (m.fairness_coeff / total_coeff), 2)
        share = models.ExpenseShare(
            expense_id=expense.id,
            user_id=m.user_id,
            amount=user_amount,
            paid_amount=0.0,
            is_settled=False,
        )
        db.add(share)

    hist = models.ExpenseHistory(
        expense_id=expense.id,
        change_desc="Создан расход и рассчитаны доли",
    )
    db.add(hist)

    # карма за создание расхода (если она у тебя ещё нужна)
    current_user.karma_points += utils.KARMA_FOR_CREATE_EXPENSE
    db.add(current_user)

    db.commit()
    db.refresh(expense)

    # ДОБАВЛЯЕМ user_name В shares перед возвратом
    for share in expense.shares:
        user = db.query(models.User).filter_by(id=share.user_id).first()
        share.user_name = user.name if user else "Unknown"

    return expense


@router.get("/group/{group_id}", response_model=List[schemas.ExpenseOut])
def list_expenses_for_group(
    group_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    member = (
        db.query(models.GroupMember)
        .filter_by(group_id=group_id, user_id=current_user.id)
        .first()
    )
    if not member:
        raise HTTPException(403, "You are not a member of this group")

    expenses = (
        db.query(models.Expense)
        .filter_by(group_id=group_id)
        .order_by(models.Expense.created_at.desc())
        .all()
    )

    for exp in expenses:
        for share in exp.shares:
            user = db.query(models.User).filter_by(id=share.user_id).first()
            share.user_name = user.name if user else "Unknown"

    return expenses


@router.post("/{expense_id}/settle")
def settle_share(
    expense_id: int,
    payment: schemas.PaymentIn,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    # находим долю пользователя по этому расходу
    share = (
        db.query(models.ExpenseShare)
        .filter_by(expense_id=expense_id, user_id=current_user.id)
        .first()
    )
    if not share:
        raise HTTPException(status_code=404, detail="Share not found")

    if share.is_settled:
        return {"status": "already settled"}

    remaining = share.amount - (share.paid_amount or 0.0)
    pay = float(payment.amount)

    # защита от переплаты/невалидных сумм
    if pay <= 0 or pay > remaining + 1e-6:
        raise HTTPException(status_code=400, detail="Invalid payment amount")

    # применяем платёж
    share.paid_amount = (share.paid_amount or 0.0) + pay

    # если закрыли полностью — начисляем дедлайн-карму и (опционально) бонус
    if share.paid_amount >= share.amount - 1e-6:
        share.is_settled = True

        expense = db.query(models.Expense).filter_by(id=expense_id).first()
        if expense and getattr(expense, "due_date", None):
            # ВАЖНО: дедлайн-карма = кол-во дней до дедлайна (или минус если просрочено)
            # Если у тебя функция называется calculate_deadline_karma — замени на неё.
            deadline_delta = utils.deadline_karma_delta(expense.due_date)
            current_user.karma_points += deadline_delta

        # если хочешь оставить бонус за факт закрытия — оставь, иначе можешь удалить
        current_user.karma_points += utils.KARMA_FOR_PROMPT_SETTLE

        # авто-штраф: за каждые -10 кармы -> +0.1 к коэффициенту
        # (и карма повышается на +10, чтобы штраф применялся дискретно)
        utils.apply_negative_karma_penalty(current_user)

        db.add(current_user)

    db.add(share)
    db.commit()

    return {"status": "ok"}


@router.delete("/{expense_id}", status_code=204)
def delete_expense(
    expense_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    expense = db.query(models.Expense).filter_by(id=expense_id).first()
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")

    member = (
        db.query(models.GroupMember)
        .filter_by(group_id=expense.group_id, user_id=current_user.id)
        .first()
    )
    if not member:
        raise HTTPException(status_code=403, detail="You are not a member of this group")

    db.query(models.ExpenseShare).filter_by(expense_id=expense_id).delete()
    db.query(models.ExpenseHistory).filter_by(expense_id=expense_id).delete()

    db.delete(expense)
    db.commit()
    return Response(status_code=204)
