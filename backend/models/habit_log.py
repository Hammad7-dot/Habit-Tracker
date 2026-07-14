from sqlalchemy import Column, Integer, Date, Boolean, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship

from database import Base


class HabitLog(Base):
    __tablename__ = "habit_logs"
    __table_args__ = (
        UniqueConstraint("habit_id", "date", name="uq_habit_date"),
    )

    id = Column(Integer, primary_key=True, index=True)
    habit_id = Column(Integer, ForeignKey("habits.id", ondelete="CASCADE"), nullable=False)
    date = Column(Date, nullable=False, index=True)
    completed = Column(Boolean, default=True)

    habit = relationship("Habit", back_populates="logs")
