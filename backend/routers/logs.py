from datetime import date as date_type

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models.user import User
from models.habit import Habit
from models.habit_log import HabitLog
from schemas.habit import HabitCompletionOut
from services.auth_service import get_current_user
from services.achievement_service import evaluate_achievements
from constants import ACHIEVEMENTS_BY_ID

router = APIRouter(tags=["Habit Completion"])


@router.post("/complete/{habit_id}", response_model=HabitCompletionOut)
def complete_habit(
    habit_id: int,
    log_date: date_type | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Toggle completion for a habit on a given date (defaults to today).

    When toggling ON, also re-evaluates the achievement engine and returns
    any newly unlocked achievements alongside the log. Toggling OFF never
    revokes achievements — once unlocked, always unlocked.
    """
    habit = db.query(Habit).filter(Habit.id == habit_id, Habit.user_id == current_user.id).first()
    if not habit:
        raise HTTPException(status_code=404, detail="Habit not found")

    target_date = log_date or date_type.today()

    log = db.query(HabitLog).filter(HabitLog.habit_id == habit_id, HabitLog.date == target_date).first()
    if log:
        # Toggle off (remove) if it already exists and is completed
        db.delete(log)
        db.commit()
        return HabitCompletionOut(id=log.id, habit_id=habit_id, date=target_date, completed=False, newly_unlocked=[])

    log = HabitLog(habit_id=habit_id, date=target_date, completed=True)
    db.add(log)
    db.commit()
    db.refresh(log)

    newly_unlocked_rows = evaluate_achievements(db, current_user.id)
    newly_unlocked = [
        {
            "id": row.achievement_id,
            "name": ACHIEVEMENTS_BY_ID[row.achievement_id].name,
            "description": ACHIEVEMENTS_BY_ID[row.achievement_id].description,
            "icon": ACHIEVEMENTS_BY_ID[row.achievement_id].icon,
        }
        for row in newly_unlocked_rows
    ]

    return HabitCompletionOut(
        id=log.id,
        habit_id=log.habit_id,
        date=log.date,
        completed=log.completed,
        newly_unlocked=newly_unlocked,
    )
