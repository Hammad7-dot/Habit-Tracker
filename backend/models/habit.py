from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from database import Base
from constants import HabitCategory, DEFAULT_COLOR, DEFAULT_ICON, DEFAULT_CATEGORY


class Habit(Base):
    __tablename__ = "habits"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    title = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    category = Column(
        SAEnum(HabitCategory, name="habit_category", native_enum=False, length=20),
        default=DEFAULT_CATEGORY,
        nullable=False,
    )
    goal = Column(Integer, default=1)  # e.g. times per day
    color = Column(String(20), default=DEFAULT_COLOR)  # hex color, from curated picker
    icon = Column(String(50), default=DEFAULT_ICON)  # Font Awesome icon class, from curated picker

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    owner = relationship("User", back_populates="habits")
    logs = relationship("HabitLog", back_populates="habit", cascade="all, delete-orphan")
