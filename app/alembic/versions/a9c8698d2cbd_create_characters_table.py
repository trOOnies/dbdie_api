"""create characters table

Revision ID: a9c8698d2cbd
Revises: 716685c809da
Create Date: 2023-05-28 22:37:07.535365

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a9c8698d2cbd'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "characters",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("name", sa.String(32), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("characters")
