"""add addons table

Revision ID: c741c4bc26e3
Revises: bc0130a80440
Create Date: 2023-06-01 21:33:06.896311

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c741c4bc26e3'
down_revision = 'bc0130a80440'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "addons",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("name", sa.String(64), nullable=False),
        sa.Column("type_id", sa.Integer, nullable=False),
        sa.Column("user_id", sa.Integer, nullable=False)
    )
    op.create_table(
        "addonstypes",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("name", sa.String(32), nullable=False)
    )

    op.create_foreign_key(
        "fk_addons_addonstypes",
        source_table="addons",
        referent_table="addonstypes",
        local_cols=["type_id"],
        remote_cols=["id"]
    )
    op.create_foreign_key(
        "fk_addons_characters",
        source_table="addons",
        referent_table="characters",
        local_cols=["user_id"],
        remote_cols=["id"]
    )


def downgrade() -> None:
    op.drop_constraint("fk_addons_characters", "addons")
    op.drop_constraint("fk_addons_addonstypes", "addons")
    op.drop_table("addonstypes")
    op.drop_table("addons")
