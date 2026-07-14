from datetime import date as date_type, timedelta
from collections import defaultdict

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from models.user import User
from models.habit import Habit
from models.habit_log import HabitLog
from services.auth_service import get_current_user

router = APIRouter(tags=["Analytics"])


@router.get("/analytics")
def get_analytics(
    days: int = 30,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    habits = db.query(Habit).filter(Habit.user_id == current_user.id).all()
    habit_ids = [h.id for h in habits]

    start_date = date_type.today() - timedelta(days=days - 1)

    logs = (
        db.query(HabitLog)
        .filter(HabitLog.habit_id.in_(habit_ids), HabitLog.date >= start_date, HabitLog.completed == True)  # noqa: E712
        .all()
        if habit_ids
        else []
    )

    # Daily counts for line/bar chart
    daily_counts: dict[str, int] = defaultdict(int)
    for i in range(days):
        d = (start_date + timedelta(days=i)).isoformat()
        daily_counts[d] = 0
    for log in logs:
        daily_counts[log.date.isoformat()] += 1

    # Category breakdown for pie chart
    category_counts: dict[str, int] = defaultdict(int)
    habit_by_id = {h.id: h for h in habits}
    for log in logs:
        habit = habit_by_id.get(log.habit_id)
        if habit:
            category_counts[habit.category.value] += 1

    # Per-habit completion rate over the period
    per_habit = []
    for habit in habits:
        completed = sum(1 for log in logs if log.habit_id == habit.id)
        rate = round((completed / days) * 100, 1)
        per_habit.append({
            "habit_id": habit.id,
            "title": habit.title,
            "color": habit.color,
            "completed_count": completed,
            "completion_rate": rate,
        })

    return {
        "period_days": days,
        "daily_completions": [{"date": d, "count": c} for d, c in sorted(daily_counts.items())],
        "category_breakdown": [{"category": c, "count": n} for c, n in category_counts.items()],
        "per_habit": per_habit,
    }


@router.get("/analytics/heatmap")
def get_calendar_heatmap(
    year: int | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    GitHub-style calendar heatmap data: one entry per day of the given year
    with a completion count and a 0-4 intensity level, for rendering a
    year-long contribution grid (Phase 4 frontend).
    """
    target_year = year or date_type.today().year
    start_date = date_type(target_year, 1, 1)
    end_date = date_type(target_year, 12, 31)

    habit_ids = [h.id for h in db.query(Habit.id).filter(Habit.user_id == current_user.id).all()]

    logs = (
        db.query(HabitLog)
        .filter(
            HabitLog.habit_id.in_(habit_ids),
            HabitLog.date >= start_date,
            HabitLog.date <= end_date,
            HabitLog.completed == True,  # noqa: E712
        )
        .all()
        if habit_ids
        else []
    )

    counts: dict[str, int] = defaultdict(int)
    for log in logs:
        counts[log.date.isoformat()] += 1

    max_count = max(counts.values(), default=0)

    def _level(count: int) -> int:
        """0 = no activity, 1-4 = quartile intensity (like GitHub's grid)."""
        if count == 0 or max_count == 0:
            return 0
        ratio = count / max_count
        if ratio <= 0.25:
            return 1
        if ratio <= 0.5:
            return 2
        if ratio <= 0.75:
            return 3
        return 4

    days = []
    cursor = start_date
    while cursor <= end_date:
        iso = cursor.isoformat()
        count = counts.get(iso, 0)
        days.append({"date": iso, "count": count, "level": _level(count)})
        cursor += timedelta(days=1)

    return {
        "year": target_year,
        "total_completions": sum(counts.values()),
        "max_day_count": max_count,
        "days": days,
    }
