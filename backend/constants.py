"""
Shared constants for habit customization: categories, icons, and colors.

Phase 2 introduces a fixed, validated vocabulary for these fields so the
frontend can render a proper picker (Phase 4) and the backend can reject
garbage input instead of silently accepting any string.
"""
from enum import Enum


class HabitCategory(str, Enum):
    HEALTH = "Health"
    FITNESS = "Fitness"
    PRODUCTIVITY = "Productivity"
    MINDFULNESS = "Mindfulness"
    LEARNING = "Learning"
    SOCIAL = "Social"
    FINANCE = "Finance"
    CREATIVITY = "Creativity"
    PERSONAL = "Personal"
    OTHER = "Other"


# Curated Font Awesome (solid) icon classes offered in the icon picker.
# Keeping this list small and deliberate makes for a coherent UI instead of
# an unbounded free-text field.
ALLOWED_ICONS: tuple[str, ...] = (
    "fa-star",
    "fa-heart",
    "fa-dumbbell",
    "fa-running",
    "fa-walking",
    "fa-bicycle",
    "fa-bed",
    "fa-glass-water",
    "fa-apple-whole",
    "fa-utensils",
    "fa-leaf",
    "fa-seedling",
    "fa-sun",
    "fa-moon",
    "fa-brain",
    "fa-om",
    "fa-book",
    "fa-graduation-cap",
    "fa-pen",
    "fa-code",
    "fa-paint-brush",
    "fa-music",
    "fa-camera",
    "fa-briefcase",
    "fa-piggy-bank",
    "fa-check-circle",
    "fa-bell",
    "fa-tooth",
    "fa-smoking-ban",
    "fa-users",
)

# Curated hex color swatches offered in the color picker.
ALLOWED_COLORS: tuple[str, ...] = (
    "#ef4444",  # red
    "#f97316",  # orange
    "#f59e0b",  # amber
    "#eab308",  # yellow
    "#84cc16",  # lime
    "#22c55e",  # green
    "#10b981",  # emerald
    "#14b8a6",  # teal
    "#06b6d4",  # cyan
    "#0ea5e9",  # sky
    "#3b82f6",  # blue
    "#6366f1",  # indigo
    "#8b5cf6",  # violet (default)
    "#a855f7",  # purple
    "#d946ef",  # fuchsia
    "#ec4899",  # pink
    "#f43f5e",  # rose
    "#64748b",  # slate
)

DEFAULT_COLOR = "#8b5cf6"
DEFAULT_ICON = "fa-star"
DEFAULT_CATEGORY = HabitCategory.PERSONAL


class AchievementType(str, Enum):
    """What kind of stat an achievement's threshold is measured against."""

    STREAK = "streak"                        # longest current streak on any single habit
    TOTAL_COMPLETIONS = "total_completions"  # lifetime completed logs across all habits
    HABIT_COUNT = "habit_count"              # number of habits created
    CATEGORY_SPREAD = "category_spread"      # distinct categories with >=1 completion
    PERFECT_DAY = "perfect_day"              # number of days where every habit was completed


class AchievementDefinition:
    """Static definition of a single achievement (not a DB row)."""

    __slots__ = ("id", "name", "description", "icon", "type", "threshold")

    def __init__(self, id: str, name: str, description: str, icon: str, type: "AchievementType", threshold: int):
        self.id = id
        self.name = name
        self.description = description
        self.icon = icon
        self.type = type
        self.threshold = threshold


# Curated, hand-picked achievements. Ordered roughly by difficulty within each type.
# Adding a new one only requires appending here — the engine in
# services/achievement_service.py evaluates all of them generically.
ACHIEVEMENTS: tuple[AchievementDefinition, ...] = (
    # Streaks
    AchievementDefinition("streak_3", "Getting Started", "Reach a 3-day streak on any habit", "fa-fire", AchievementType.STREAK, 3),
    AchievementDefinition("streak_7", "One Week Strong", "Reach a 7-day streak on any habit", "fa-fire", AchievementType.STREAK, 7),
    AchievementDefinition("streak_14", "Two Week Warrior", "Reach a 14-day streak on any habit", "fa-fire", AchievementType.STREAK, 14),
    AchievementDefinition("streak_30", "Monthly Master", "Reach a 30-day streak on any habit", "fa-fire", AchievementType.STREAK, 30),
    AchievementDefinition("streak_100", "Centurion", "Reach a 100-day streak on any habit", "fa-fire", AchievementType.STREAK, 100),
    # Total completions
    AchievementDefinition("completions_10", "First Steps", "Log 10 total completions", "fa-check-circle", AchievementType.TOTAL_COMPLETIONS, 10),
    AchievementDefinition("completions_50", "Building Momentum", "Log 50 total completions", "fa-check-circle", AchievementType.TOTAL_COMPLETIONS, 50),
    AchievementDefinition("completions_100", "Century Club", "Log 100 total completions", "fa-check-circle", AchievementType.TOTAL_COMPLETIONS, 100),
    AchievementDefinition("completions_500", "Habit Master", "Log 500 total completions", "fa-check-circle", AchievementType.TOTAL_COMPLETIONS, 500),
    # Habit count
    AchievementDefinition("habits_3", "Multitasker", "Create 3 habits", "fa-star", AchievementType.HABIT_COUNT, 3),
    AchievementDefinition("habits_10", "Habit Collector", "Create 10 habits", "fa-star", AchievementType.HABIT_COUNT, 10),
    # Category spread
    AchievementDefinition("categories_3", "Well Rounded", "Complete habits in 3 different categories", "fa-leaf", AchievementType.CATEGORY_SPREAD, 3),
    AchievementDefinition("categories_5", "Renaissance Person", "Complete habits in 5 different categories", "fa-leaf", AchievementType.CATEGORY_SPREAD, 5),
    # Perfect days
    AchievementDefinition("perfect_day_1", "Clean Sweep", "Complete every habit on a single day", "fa-om", AchievementType.PERFECT_DAY, 1),
    AchievementDefinition("perfect_day_7", "Perfect Week", "Have 7 perfect days (not necessarily consecutive)", "fa-om", AchievementType.PERFECT_DAY, 7),
    AchievementDefinition("perfect_day_30", "Flawless Month", "Have 30 perfect days", "fa-om", AchievementType.PERFECT_DAY, 30),
)

ACHIEVEMENTS_BY_ID: dict[str, AchievementDefinition] = {a.id: a for a in ACHIEVEMENTS}
