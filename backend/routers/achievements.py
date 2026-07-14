from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from models.user import User
from models.achievement import UserAchievement
from constants import ACHIEVEMENTS
from schemas.achievement import AchievementOut, AchievementsSummaryOut, NewlyUnlockedOut
from services.auth_service import get_current_user
from services.achievement_service import compute_user_stats, evaluate_achievements

router = APIRouter(prefix="/achievements", tags=["Achievements"])


@router.get("", response_model=AchievementsSummaryOut)
def list_achievements(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Full achievement catalog merged with this user's progress and unlock status."""
    stats = compute_user_stats(db, current_user.id)

    unlocked_rows = {
        row.achievement_id: row.unlocked_at
        for row in db.query(UserAchievement).filter(UserAchievement.user_id == current_user.id).all()
    }

    achievements = []
    for definition in ACHIEVEMENTS:
        unlocked_at = unlocked_rows.get(definition.id)
        achievements.append(
            AchievementOut(
                id=definition.id,
                name=definition.name,
                description=definition.description,
                icon=definition.icon,
                type=definition.type,
                threshold=definition.threshold,
                current_value=stats.get(definition.type, 0),
                unlocked=unlocked_at is not None,
                unlocked_at=unlocked_at,
            )
        )

    return AchievementsSummaryOut(
        achievements=achievements,
        unlocked_count=len(unlocked_rows),
        total_count=len(ACHIEVEMENTS),
    )


@router.post("/evaluate", response_model=list[NewlyUnlockedOut])
def evaluate(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Re-checks the user's stats against all achievements and unlocks any newly
    earned ones. Also called automatically after completing a habit
    (see POST /complete/{habit_id}) — exposed here too so the frontend can
    force a re-check (e.g. after bulk edits) without completing a habit.
    """
    newly_unlocked = evaluate_achievements(db, current_user.id)
    by_id = {a.id: a for a in ACHIEVEMENTS}
    return [
        NewlyUnlockedOut(
            id=row.achievement_id,
            name=by_id[row.achievement_id].name,
            description=by_id[row.achievement_id].description,
            icon=by_id[row.achievement_id].icon,
        )
        for row in newly_unlocked
    ]
