"""align cardinality and table names

Revision ID: 3c40e02028e4
Revises: e1000e0cae9e
Create Date: 2024-07-10 19:03:03.690161

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "3c40e02028e4"
down_revision = "e1000e0cae9e"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.rename_table("addonstypes", "addons_types")
    op.rename_table("characters", "character")
    op.rename_table("items", "item")
    op.rename_table("itemstypes", "item_types")
    op.rename_table("offerings", "offering")
    op.rename_table("offeringstypes", "offering_types")


def downgrade() -> None:
    op.rename_table("addons_types", "addonstypes")
    op.rename_table("character", "characters")
    op.rename_table("item", "items")
    op.rename_table("item_types", "itemstypes")
    op.rename_table("offering", "offerings")
    op.rename_table("offering_types", "offeringstypes")
