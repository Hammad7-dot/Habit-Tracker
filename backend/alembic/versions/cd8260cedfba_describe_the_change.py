<<<<<<< HEAD
"""describe the change

Revision ID: cd8260cedfba
Revises: 0001_initial
Create Date: 2026-07-15 00:17:05.307166

"""
=======

>>>>>>> 67dc7449e9306e1041dd90249aae478f9d1548fc
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


<<<<<<< HEAD
# revision identifiers, used by Alembic.
=======
>>>>>>> 67dc7449e9306e1041dd90249aae478f9d1548fc
revision: str = 'cd8260cedfba'
down_revision: Union[str, None] = '0001_initial'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
<<<<<<< HEAD
    op.add_column(
        "habits",
        sa.Column("reminder_enabled", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.add_column(
        "habits",
        sa.Column("reminder_time", sa.Time(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("habits", "reminder_time")
    op.drop_column("habits", "reminder_enabled")
=======
    
    op.add_column("habits", sa.Column("reminder_enabled", sa.Boolean(), nullable=False, server_default=sa.false()))
    op.add_column("habits", sa.Column("reminder_time", sa.Time(), nullable=True))

    pass




def downgrade() -> None:
   
    op.drop_column("habits", "reminder_time")
    op.drop_column("habits", "reminder_enabled")

    pass

>>>>>>> 67dc7449e9306e1041dd90249aae478f9d1548fc
