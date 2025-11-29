# backend/app/routers/groups.py

from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from .. import models, schemas, utils
from ..deps import get_db, get_current_user

router = APIRouter(prefix="/groups", tags=["groups"])


@router.post("/", response_model=schemas.GroupOut)
def create_group(
    group_in: schemas.GroupCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    # создаём саму группу
    group = models.Group(
        name=group_in.name,
        description=group_in.description,
        owner_id=current_user.id,
    )
    db.add(group)
    db.commit()
    db.refresh(group)

    # создатель сразу становится участником с коэффициентом по доходу
    member = models.GroupMember(
        group_id=group.id,
        user_id=current_user.id,
        fairness_coeff=utils.get_fairness_coeff_for_income(
            current_user.income_category
        ),
    )
    db.add(member)
    db.commit()

    return group


@router.get("/", response_model=List[schemas.GroupOut])
def list_my_groups(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    groups = (
        db.query(models.Group)
        .join(models.GroupMember, models.Group.id == models.GroupMember.group_id)
        .filter(models.GroupMember.user_id == current_user.id)
        .all()
    )
    return groups


@router.get("/search", response_model=List[schemas.GroupOut])
def search_groups(
    q: str = Query(..., min_length=1, description="Часть названия группы"),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    pattern = f"%{q}%"
    groups = (
        db.query(models.Group)
        .filter(models.Group.name.ilike(pattern))
        .limit(20)
        .all()
    )
    return groups


@router.post("/{group_id}/join", response_model=schemas.GroupOut)
def join_group(
    group_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    group = db.query(models.Group).filter_by(id=group_id).first()
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")

    existing = (
        db.query(models.GroupMember)
        .filter_by(group_id=group_id, user_id=current_user.id)
        .first()
    )
    if existing:
        return group

    member = models.GroupMember(
        group_id=group_id,
        user_id=current_user.id,
        fairness_coeff=utils.get_fairness_coeff_for_income(
            current_user.income_category
        ),
    )
    db.add(member)
    db.commit()

    return group
