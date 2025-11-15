from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import schemas, models, utils
from ..deps import get_db, get_current_user

router = APIRouter(prefix="/groups", tags=["groups"])


@router.post("/", response_model=schemas.GroupOut)
def create_group(
    group_in: schemas.GroupCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    group = models.Group(
        name=group_in.name,
        description=group_in.description,
        owner_id=current_user.id,
    )
    db.add(group)
    db.commit()
    db.refresh(group)

    # владелец автоматически становится участником
    member = models.GroupMember(
        user_id=current_user.id,
        group_id=group.id,
        fairness_coeff=utils.income_to_coeff(current_user.income_category)
    )
    db.add(member)
    db.commit()

    return group


@router.post("/{group_id}/members/{user_id}")
def add_member(
    group_id: int,
    user_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    group = db.query(models.Group).filter_by(id=group_id).first()
    if not group:
        raise HTTPException(404, "Group not found")

    user = db.query(models.User).filter_by(id=user_id).first()
    if not user:
        raise HTTPException(404, "User not found")

    # коэффициент по выбранной пользователем категории дохода
    coeff = utils.income_to_coeff(user.income_category)

    member = models.GroupMember(
        user_id=user_id,
        group_id=group_id,
        fairness_coeff=coeff,
    )
    db.add(member)
    db.commit()
    return {"status": "ok"}
