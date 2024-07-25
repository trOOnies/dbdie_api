"""add items table

Revision ID: bc0130a80440
Revises: 7a9444ee8c15
Create Date: 2023-06-01 21:20:52.724756

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "bc0130a80440"
down_revision = "7a9444ee8c15"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "items",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("name", sa.String(64), nullable=False),
        sa.Column("type_id", sa.Integer, nullable=False),
    )
    op.create_table(
        "itemstypes",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("name", sa.String(32), nullable=False),
    )

    op.create_foreign_key(
        "fk_items_itemstypes",
        source_table="items",
        referent_table="itemstypes",
        local_cols=["type_id"],
        remote_cols=["id"],
    )


def downgrade() -> None:
    op.drop_constraint("fk_items_itemstypes", "items")
    op.drop_table("itemstypes")
    op.drop_table("items")
