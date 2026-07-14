from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models.user import User
from models.habit import Habit
from models.habit_log import HabitLog
from schemas.user import UserOut, UserUpdate, ChangePassword
from services.auth_service import get_current_user
from utils.security import verify_password, hash_password

router = APIRouter(prefix="/profile", tags=["Profile"])


@router.get("", response_model=UserOut)
def get_profile(current_user: User = Depends(get_current_user)):
    return current_user


@router.put("", response_model=UserOut)
def update_profile(
    payload: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(current_user, field, value)
    db.commit()
    db.refresh(current_user)
    return current_user


@router.post("/change-password")
def change_password(
    payload: ChangePassword,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not verify_password(payload.current_password, current_user.password_hash):
        raise HTTPException(status_code=400, detail="Current password is incorrect")
    current_user.password_hash = hash_password(payload.new_password)
    db.commit()
    return {"message": "Password updated successfully"}


@router.get("/stats")
def get_profile_stats(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    total_habits = db.query(Habit).filter(Habit.user_id == current_user.id).count()
    habit_ids = [h.id for h in db.query(Habit.id).filter(Habit.user_id == current_user.id).all()]
    total_completions = (
        db.query(HabitLog)
        .filter(HabitLog.habit_id.in_(habit_ids), HabitLog.completed == True)  # noqa: E712
        .count()
        if habit_ids
        else 0
    )
    return {
        "total_habits": total_habits,
        "total_completions": total_completions,
        "member_since": current_user.created_at,
    }
