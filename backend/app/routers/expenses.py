from fastapi import APIRouter, Depends, HTTPException
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

    expense = models.Expense(
        group_id=group_id,
        creator_id=current_user.id,
        amount=expense_in.amount,
        description=expense_in.description,
        category_id=expense_in.category_id
    )
    db.add(expense)
    db.commit()
    db.refresh(expense)

    # расчёт долей по коэффициентам
    members = db.query(models.GroupMember).filter_by(group_id=group_id).all()
    total_coeff = sum(m.fairness_coeff for m in members)
    shares = []
    for m in members:
        user_amount = round(expense.amount * (m.fairness_coeff / total_coeff), 2)
        share = models.ExpenseShare(
            expense_id=expense.id,
            user_id=m.user_id,
            amount=user_amount,
            is_settled=False
        )
        db.add(share)
        shares.append(share)

    # история
    hist = models.ExpenseHistory(
        expense_id=expense.id,
        change_desc="Создан расход и рассчитаны доли"
    )
    db.add(hist)

    # карма за активные действия (создал расход) — п. 10.2
    current_user.karma_points += utils.KARMA_FOR_CREATE_EXPENSE
    db.add(current_user)

    db.commit()

    db.refresh(expense)

    return expense


@router.post("/{expense_id}/settle")
def settle_share(
    expense_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    share = db.query(models.ExpenseShare).filter_by(
        expense_id=expense_id, user_id=current_user.id
    ).first()
    if not share:
        raise HTTPException(404, "Share not found")
    if share.is_settled:
        return {"status": "already settled"}

    share.is_settled = True

    # карма за своевременный расчёт
    current_user.karma_points += utils.KARMA_FOR_PROMPT_SETTLE

    hist = models.ExpenseHistory(
        expense_id=expense_id,
        change_desc=f"Пользователь {current_user.id} закрыл свою долю"
    )
    db.add(hist)
    db.add(current_user)
    db.commit()
    return {"status": "ok"}
