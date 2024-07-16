"""add base_char_id column for legendaries

Revision ID: e1000e0cae9e
Revises: be1f67f8a086
Create Date: 2024-06-22 22:50:41.792781

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e1000e0cae9e'
down_revision = 'be1f67f8a086'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "characters",
        sa.Column("base_char_id", sa.Integer(), nullable=True)
    )


def downgrade() -> None:
    op.drop_column("characters", "base_char_id")
