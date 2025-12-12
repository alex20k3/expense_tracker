from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..deps import get_db, get_current_user
from .. import models

router = APIRouter(prefix="/karma", tags=["karma"])


@router.get("/me")
def my_karma(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    return {
        "user_id": current_user.id,
        "karma_points": current_user.karma_points
    }

@router.post("/use/forgive-debt")
def forgive_all_debts_with_karma(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    if current_user.karma_points < 100:
        raise HTTPException(400, "Недостаточно кармы (нужно 100)")

    shares = db.query(models.ExpenseShare).filter_by(user_id=current_user.id).all()

    for s in shares:
        s.paid_amount = s.amount
        s.is_settled = True

    current_user.karma_points -= 100

    db.commit()
    return {"status": "ok"}

@router.post("/use/lower-coeff")
def lower_coeff(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    if current_user.karma_points < 150:
        raise HTTPException(400, "Недостаточно кармы (нужно 150)")

    current_user.fairness_coeff = max(0.1, current_user.fairness_coeff - 0.1)
    current_user.karma_points -= 150

    db.commit()
    return {"status": "ok"}

@router.post("/apply-negative-penalty")
def penalty_for_negative_karma(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    if current_user.karma_points > -10:
        raise HTTPException(400, "Недостаточно минусовой кармы (нужно ≤ -10)")

    current_user.fairness_coeff += 0.1

    # можно обнулить карму или оставить как есть — зависит от ТЗ
    current_user.karma_points = 0

    db.commit()
    return {"status": "ok"}
