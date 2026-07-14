from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "0001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

HABIT_CATEGORIES = (
    "Health", "Fitness", "Productivity", "Mindfulness", "Learning",
    "Social", "Finance", "Creativity", "Personal", "Other",
)


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("username", sa.String(length=50), nullable=False),
        sa.Column("email", sa.String(length=120), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("avatar_url", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_users_username", "users", ["username"], unique=True)
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    op.create_index("ix_users_id", "users", ["id"])


    op.create_table(
        "habits",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("title", sa.String(length=100), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column(
            "category",
            sa.String(length=20),
            nullable=False,
            server_default="Personal",
        ),
        sa.Column("goal", sa.Integer(), nullable=True, server_default="1"),
        sa.Column("color", sa.String(length=20), nullable=True, server_default="#8b5cf6"),
        sa.Column("icon", sa.String(length=50), nullable=True, server_default="fa-star"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint(
            "category IN (" + ", ".join(f"'{c}'" for c in HABIT_CATEGORIES) + ")",
            name="ck_habits_category",
        ),
    )

    op.create_index("ix_habits_id", "habits", ["id"])


    op.create_table(
        "habit_logs",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("habit_id", sa.Integer(), sa.ForeignKey("habits.id", ondelete="CASCADE"), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("completed", sa.Boolean(), nullable=True, server_default=sa.true()),
        sa.UniqueConstraint("habit_id", "date", name="uq_habit_date"),
    )

    op.create_index("ix_habit_logs_id", "habit_logs", ["id"])

    op.create_index("ix_habit_logs_date", "habit_logs", ["date"])

    op.create_table(
        "user_achievements",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("achievement_id", sa.String(length=50), nullable=False),
        sa.Column("unlocked_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.UniqueConstraint("user_id", "achievement_id", name="uq_user_achievement"),
    )

    op.create_index("ix_user_achievements_id", "user_achievements", ["id"])

    op.create_index("ix_user_achievements_user_id", "user_achievements", ["user_id"])
    op.create_index("ix_user_achievements_achievement_id", "user_achievements", ["achievement_id"])


def downgrade() -> None:
    op.drop_table("user_achievements")
    op.drop_table("habit_logs")
    op.drop_table("habits")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_index("ix_users_username", table_name="users")
    op.drop_table("users")
