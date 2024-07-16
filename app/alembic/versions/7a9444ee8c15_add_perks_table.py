"""add perks table

Revision ID: 7a9444ee8c15
Revises: e06ff61fada2
Create Date: 2023-06-01 20:45:24.763378

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7a9444ee8c15'
down_revision = 'e06ff61fada2'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "perks",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("name", sa.String(64), nullable=False),
        sa.Column("character_id", sa.Integer, nullable=False)
    )
    op.create_foreign_key(
        "fk_perks_characters",
        source_table="perks",
        referent_table="characters",
        local_cols=["character_id"],
        remote_cols=["id"]
    )


def downgrade() -> None:
    op.drop_constraint("fk_perks_characters", "perks")
    op.drop_table("perks")
