from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from models.user import User
from models.habit import Habit
from schemas.habit import HabitCreate, HabitUpdate, HabitOut, HabitOptionsOut
from services.auth_service import get_current_user
from constants import HabitCategory, ALLOWED_ICONS, ALLOWED_COLORS

router = APIRouter(prefix="/habits", tags=["Habits"])


@router.get("/options", response_model=HabitOptionsOut)
def get_habit_options():
    """Valid categories/icons/colors for the habit create/edit picker UI."""
    return HabitOptionsOut(
        categories=[c.value for c in HabitCategory],
        icons=list(ALLOWED_ICONS),
        colors=list(ALLOWED_COLORS),
    )


@router.get("", response_model=List[HabitOut])
def list_habits(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(Habit).filter(Habit.user_id == current_user.id).order_by(Habit.created_at.desc()).all()


@router.post("", response_model=HabitOut, status_code=status.HTTP_201_CREATED)
def create_habit(payload: HabitCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    habit = Habit(user_id=current_user.id, **payload.model_dump())
    db.add(habit)
    db.commit()
    db.refresh(habit)
    return habit


def _get_owned_habit(habit_id: int, db: Session, current_user: User) -> Habit:
    habit = db.query(Habit).filter(Habit.id == habit_id, Habit.user_id == current_user.id).first()
    if not habit:
        raise HTTPException(status_code=404, detail="Habit not found")
    return habit


@router.put("/{habit_id}", response_model=HabitOut)
def update_habit(habit_id: int, payload: HabitUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    habit = _get_owned_habit(habit_id, db, current_user)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(habit, field, value)
    db.commit()
    db.refresh(habit)
    return habit


@router.delete("/{habit_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_habit(habit_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    habit = _get_owned_habit(habit_id, db, current_user)
    db.delete(habit)
    db.commit()
    return None
