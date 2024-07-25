"""add is_killer column

Revision ID: e06ff61fada2
Revises: a9c8698d2cbd
Create Date: 2023-05-28 22:46:38.597984

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "e06ff61fada2"
down_revision = "a9c8698d2cbd"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("characters", sa.Column("is_killer", sa.Boolean(), nullable=True))


def downgrade() -> None:
    op.drop_column("characters", "is_killer")
