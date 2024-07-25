"""add status table

Revision ID: 8b73a1960cc2
Revises: 3954dfa4f55a
Create Date: 2023-09-15 21:32:09.037553

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "8b73a1960cc2"
down_revision = "3954dfa4f55a"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "status",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("name", sa.String(32), nullable=False),
        sa.Column("character_id", sa.Integer, nullable=False),
    )
    op.create_foreign_key(
        "fk_status_characters",
        source_table="status",
        referent_table="characters",
        local_cols=["character_id"],
        remote_cols=["id"],
    )


def downgrade() -> None:
    op.drop_constraint("fk_status_characters", "status")
    op.drop_table("status")
