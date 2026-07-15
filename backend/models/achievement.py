from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from database import Base


class UserAchievement(Base):
    """
    Records that a user has unlocked a given achievement.

    `achievement_id` references the static `id` field of an
    AchievementDefinition in constants.ACHIEVEMENTS — there's no
    achievements table since the catalog is fixed, curated, and versioned
    in code rather than user-editable data.
    """

    __tablename__ = "user_achievements"
    __table_args__ = (
        UniqueConstraint("user_id", "achievement_id", name="uq_user_achievement"),
    )

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    achievement_id = Column(String(50), nullable=False, index=True)
    unlocked_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="achievements")
