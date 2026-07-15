from pydantic import BaseModel, Field, ConfigDict, field_validator
from datetime import datetime, date, time
from typing import Optional

from constants import HabitCategory, ALLOWED_ICONS, ALLOWED_COLORS, DEFAULT_COLOR, DEFAULT_ICON


def _validate_icon(icon: str) -> str:
    if icon not in ALLOWED_ICONS:
        raise ValueError(
            f"'{icon}' is not a supported icon. Choose one of: {', '.join(ALLOWED_ICONS)}"
        )
    return icon


def _validate_color(color: str) -> str:
    if color not in ALLOWED_COLORS:
        raise ValueError(
            f"'{color}' is not a supported color. Choose one of: {', '.join(ALLOWED_COLORS)}"
        )
    return color


class HabitCreate(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    description: Optional[str] = None
    category: HabitCategory = HabitCategory.PERSONAL
    goal: int = Field(default=1, ge=1)
    color: str = DEFAULT_COLOR
    icon: str = DEFAULT_ICON
    reminder_enabled: bool = False
    reminder_time: Optional[time] = None

    @field_validator("icon")
    @classmethod
    def icon_must_be_supported(cls, v: str) -> str:
        return _validate_icon(v)

    @field_validator("color")
    @classmethod
    def color_must_be_supported(cls, v: str) -> str:
        return _validate_color(v)


class HabitUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=100)
    description: Optional[str] = None
    category: Optional[HabitCategory] = None
    goal: Optional[int] = Field(default=None, ge=1)
    color: Optional[str] = None
    icon: Optional[str] = None
    reminder_enabled: Optional[bool] = None
    reminder_time: Optional[time] = None

    @field_validator("icon")
    @classmethod
    def icon_must_be_supported(cls, v: Optional[str]) -> Optional[str]:
        return _validate_icon(v) if v is not None else v

    @field_validator("color")
    @classmethod
    def color_must_be_supported(cls, v: Optional[str]) -> Optional[str]:
        return _validate_color(v) if v is not None else v


class HabitOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    title: str
    description: Optional[str] = None
    category: HabitCategory
    goal: int
    color: str
    icon: str
    reminder_enabled: bool = False
    reminder_time: Optional[time] = None
    created_at: datetime


class HabitLogOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    habit_id: int
    date: date
    completed: bool


class NewlyUnlockedAchievement(BaseModel):
    id: str
    name: str
    description: str
    icon: str


class HabitCompletionOut(HabitLogOut):
    """Response for POST /complete/{habit_id} — the log plus any achievements it unlocked."""

    newly_unlocked: list[NewlyUnlockedAchievement] = []


class HabitWithStats(HabitOut):
    current_streak: int = 0
    longest_streak: int = 0
    completed_today: bool = False
    completion_rate: float = 0.0


class HabitOptionsOut(BaseModel):
    """Picker options for the habit creation/edit UI (Phase 4 frontend)."""

    categories: list[str]
    icons: list[str]
    colors: list[str]
