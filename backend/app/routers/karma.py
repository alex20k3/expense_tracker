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
