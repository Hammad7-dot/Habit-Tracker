"""
Achievement engine (Phase 3).

Achievements are defined statically in constants.ACHIEVEMENTS. This module:
  1. Computes the current value of each AchievementType stat for a user.
  2. Compares those values against every achievement's threshold.
  3. Persists newly-crossed thresholds as UserAchievement rows.

Evaluation is cheap enough to run synchronously right after a habit is
completed (see routers/logs.py) — it's a handful of aggregate queries
scoped to one user, not a background job.
"""
from collections import defaultdict
from datetime import date as date_type

from sqlalchemy.orm import Session

from constants import ACHIEVEMENTS, AchievementType
from models.habit import Habit
from models.habit_log import HabitLog
from models.achievement import UserAchievement


def _longest_current_streak_across_habits(db: Session, habit_ids: list[int]) -> int:
    """Longest of each habit's current (active, ending today-or-yesterday) streak."""
    if not habit_ids:
        return 0

    best = 0
    for habit_id in habit_ids:
        dates = {
            row.date
            for row in db.query(HabitLog.date)
            .filter(HabitLog.habit_id == habit_id, HabitLog.completed == True)  # noqa: E712
            .all()
        }
        if not dates:
            continue
        from datetime import timedelta

        cursor = date_type.today()
        if cursor not in dates:
            cursor -= timedelta(days=1)
        streak = 0
        while cursor in dates:
            streak += 1
            cursor -= timedelta(days=1)
        best = max(best, streak)
    return best


def _perfect_day_count(db: Session, habit_ids: list[int]) -> int:
    """
    Number of distinct days on which EVERY habit the user owned at that time
    was completed. We approximate "owned at that time" as "owned now" — good
    enough for a gamification feature and much simpler than tracking habit
    lifecycle history.
    """
    if not habit_ids:
        return 0

    logs = (
        db.query(HabitLog.date, HabitLog.habit_id)
        .filter(HabitLog.habit_id.in_(habit_ids), HabitLog.completed == True)  # noqa: E712
        .all()
    )
    completed_by_day: dict[date_type, set[int]] = defaultdict(set)
    for log_date, habit_id in logs:
        completed_by_day[log_date].add(habit_id)

    total_habits = len(habit_ids)
    return sum(1 for habit_set in completed_by_day.values() if len(habit_set) == total_habits)


def compute_user_stats(db: Session, user_id: int) -> dict["AchievementType", int]:
    """Returns the current value for each AchievementType stat, for one user."""
    habits = db.query(Habit).filter(Habit.user_id == user_id).all()
    habit_ids = [h.id for h in habits]

    total_completions = (
        db.query(HabitLog)
        .filter(HabitLog.habit_id.in_(habit_ids), HabitLog.completed == True)  # noqa: E712
        .count()
        if habit_ids
        else 0
    )

    category_spread = 0
    if habit_ids:
        completed_habit_ids = {
            row.habit_id
            for row in db.query(HabitLog.habit_id)
            .filter(HabitLog.habit_id.in_(habit_ids), HabitLog.completed == True)  # noqa: E712
            .distinct()
            .all()
        }
        habit_by_id = {h.id: h for h in habits}
        category_spread = len({habit_by_id[hid].category for hid in completed_habit_ids if hid in habit_by_id})

    return {
        AchievementType.STREAK: _longest_current_streak_across_habits(db, habit_ids),
        AchievementType.TOTAL_COMPLETIONS: total_completions,
        AchievementType.HABIT_COUNT: len(habits),
        AchievementType.CATEGORY_SPREAD: category_spread,
        AchievementType.PERFECT_DAY: _perfect_day_count(db, habit_ids),
    }


def evaluate_achievements(db: Session, user_id: int) -> list[UserAchievement]:
    """
    Checks the user's current stats against every achievement definition and
    persists any newly-crossed thresholds. Returns only the newly unlocked
    UserAchievement rows (empty list if nothing new).
    """
    stats = compute_user_stats(db, user_id)

    already_unlocked = {
        row.achievement_id
        for row in db.query(UserAchievement.achievement_id).filter(UserAchievement.user_id == user_id).all()
    }

    newly_unlocked: list[UserAchievement] = []
    for definition in ACHIEVEMENTS:
        if definition.id in already_unlocked:
            continue
        if stats.get(definition.type, 0) >= definition.threshold:
            row = UserAchievement(user_id=user_id, achievement_id=definition.id)
            db.add(row)
            newly_unlocked.append(row)

    if newly_unlocked:
        db.commit()
        for row in newly_unlocked:
            db.refresh(row)

    return newly_unlocked
