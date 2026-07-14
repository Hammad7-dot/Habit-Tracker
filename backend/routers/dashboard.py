from datetime import date as date_type, timedelta

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from models.user import User
from models.habit import Habit
from models.habit_log import HabitLog
from services.auth_service import get_current_user

router = APIRouter(tags=["Dashboard"])


def _compute_streak(db: Session, habit_id: int) -> tuple[int, int]:
    """Returns (current_streak, longest_streak) in days, based on completed logs."""
    logs = (
        db.query(HabitLog)
        .filter(HabitLog.habit_id == habit_id, HabitLog.completed == True)  # noqa: E712
        .order_by(HabitLog.date.desc())
        .all()
    )
    if not logs:
        return 0, 0

    dates = sorted({log.date for log in logs}, reverse=True)

    # current streak: consecutive days counting back from today (or yesterday)
    current = 0
    cursor = date_type.today()
    date_set = set(dates)
    while cursor in date_set:
        current += 1
        cursor -= timedelta(days=1)
    if current == 0 and (date_type.today() - timedelta(days=1)) in date_set:
        # allow streak to still count if today not yet logged
        cursor = date_type.today() - timedelta(days=1)
        while cursor in date_set:
            current += 1
            cursor -= timedelta(days=1)

    # longest streak: scan sorted ascending
    asc_dates = sorted(dates)
    longest = 1
    run = 1
    for i in range(1, len(asc_dates)):
        if asc_dates[i] - asc_dates[i - 1] == timedelta(days=1):
            run += 1
        else:
            run = 1
        longest = max(longest, run)
    longest = max(longest, current)

    return current, longest


@router.get("/dashboard")
def get_dashboard(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    habits = db.query(Habit).filter(Habit.user_id == current_user.id).all()
    today = date_type.today()

    today_habits = []
    total_current_streak = 0
    total_longest_streak = 0
    completed_today_count = 0

    for habit in habits:
        current_streak, longest_streak = _compute_streak(db, habit.id)
        completed_today = (
            db.query(HabitLog)
            .filter(HabitLog.habit_id == habit.id, HabitLog.date == today, HabitLog.completed == True)  # noqa: E712
            .first()
            is not None
        )
        if completed_today:
            completed_today_count += 1

        total_current_streak = max(total_current_streak, current_streak)
        total_longest_streak = max(total_longest_streak, longest_streak)

        today_habits.append({
            "id": habit.id,
            "title": habit.title,
            "icon": habit.icon,
            "color": habit.color,
            "category": habit.category.value,
            "completed_today": completed_today,
            "current_streak": current_streak,
            "longest_streak": longest_streak,
        })

    completion_pct = round((completed_today_count / len(habits)) * 100, 1) if habits else 0.0

    return {
        "today_habits": today_habits,
        "current_streak": total_current_streak,
        "longest_streak": total_longest_streak,
        "completion_percentage": completion_pct,
        "total_habits": len(habits),
        "completed_today": completed_today_count,
    }
