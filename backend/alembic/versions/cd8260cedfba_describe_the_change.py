
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa



# revision identifiers, used by Alembic.

revision: str = 'cd8260cedfba'
down_revision: Union[str, None] = '0001_initial'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:

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

    
    op.add_column("habits", sa.Column("reminder_enabled", sa.Boolean(), nullable=False, server_default=sa.false()))
    op.add_column("habits", sa.Column("reminder_time", sa.Time(), nullable=True))

    pass




def downgrade() -> None:
   
    op.drop_column("habits", "reminder_time")
    op.drop_column("habits", "reminder_enabled")

    pass


