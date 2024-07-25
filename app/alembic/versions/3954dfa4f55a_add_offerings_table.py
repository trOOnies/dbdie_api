"""add offerings table

Revision ID: 3954dfa4f55a
Revises: c741c4bc26e3
Create Date: 2023-06-01 22:36:11.465836

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "3954dfa4f55a"
down_revision = "c741c4bc26e3"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "offerings",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("name", sa.String(64), nullable=False),
        sa.Column("type_id", sa.Integer, nullable=False),
        sa.Column("user_id", sa.Integer, nullable=False),
    )
    op.create_table(
        "offeringstypes",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("name", sa.String(32), nullable=False),
    )

    op.create_foreign_key(
        "fk_offerings_offeringstypes",
        source_table="offerings",
        referent_table="offeringstypes",
        local_cols=["type_id"],
        remote_cols=["id"],
    )
    op.create_foreign_key(
        "fk_offerings_characters",
        source_table="offerings",
        referent_table="characters",
        local_cols=["user_id"],
        remote_cols=["id"],
    )


def downgrade() -> None:
    op.drop_constraint("fk_offerings_characters", "offerings")
    op.drop_constraint("fk_offerings_offeringstypes", "offerings")
    op.drop_table("offeringstypes")
    op.drop_table("offerings")
