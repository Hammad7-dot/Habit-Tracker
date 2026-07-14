from datetime import datetime
from typing import Optional

from pydantic import BaseModel, computed_field

from constants import AchievementType


class AchievementOut(BaseModel):
    """A single achievement definition merged with the current user's progress."""

    id: str
    name: str
    description: str
    icon: str
    type: AchievementType
    threshold: int
    current_value: int
    unlocked: bool
    unlocked_at: Optional[datetime] = None

    @computed_field
    @property
    def progress_percentage(self) -> float:
        if self.threshold <= 0:
            return 100.0
        return round(min(self.current_value / self.threshold, 1.0) * 100, 1)


class AchievementsSummaryOut(BaseModel):
    achievements: list[AchievementOut]
    unlocked_count: int
    total_count: int


class NewlyUnlockedOut(BaseModel):
    """Returned inline from actions (e.g. completing a habit) that can trigger unlocks."""

    id: str
    name: str
    description: str
    icon: str
