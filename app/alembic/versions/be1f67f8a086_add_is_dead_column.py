"""add is_dead column

Revision ID: be1f67f8a086
Revises: 8b73a1960cc2
Create Date: 2023-09-15 21:46:04.738472

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'be1f67f8a086'
down_revision = '8b73a1960cc2'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "status",
        sa.Column("is_dead", sa.Boolean(), nullable=True)
    )


def downgrade() -> None:
    op.drop_column("status", "is_dead")
