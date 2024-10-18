"""SQLAlchemy model definitions for groupings."""

from sqlalchemy import Boolean as Bool
from sqlalchemy import Column as C
from sqlalchemy import Date
from sqlalchemy import ForeignKey as FK
from sqlalchemy import Integer as Int
from sqlalchemy import SmallInteger as SmallInt
from sqlalchemy import String as Str
from sqlalchemy.orm import relationship as rel
from sqlalchemy.sql.expression import text
from sqlalchemy.sql.sqltypes import TIMESTAMP

from backbone.database import Base
from backbone.models.helpers import DBDVersion  # noqa: F401
from backbone.models.objects import Extractor, User  # noqa: F401
from backbone.options import TABLE_NAMES as TN


class Match(Base):
    """SQLAlchemy DBD match model."""
    __tablename__ = TN.MATCHES

    id       = C(Int, nullable=False, primary_key=True)
    filename = C(Str, nullable=False)

    match_date   = C(Date, nullable=True)
    dbdv_id      = C(Int, FK(f"{TN.DBD_VERSION}.id"), nullable=True)
    dbdv         = rel("DBDVersion")

    special_mode = C(Bool,     nullable=True)
    kills        = C(SmallInt, nullable=True)

    date_created = C(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=text("now()"),
    )
    date_modified = C(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=text("now()"),
    )

    user_id   = C(SmallInt, FK(f"{TN.USER}.id"),      nullable=True)
    extr_id   = C(SmallInt, FK(f"{TN.EXTRACTOR}.id"), nullable=True)
    user      = rel("User")
    extractor = rel("Extractor")


class Labels(Base):
    """SQLAlchemy predictables labels model."""
    __tablename__ = TN.LABELS

    match_id  = C(
        Int,
        FK(f"{TN.MATCHES}.id"),
        primary_key=True,
        nullable=False,
    )
    match     = rel("Match")
    player_id = C(SmallInt, nullable=False, primary_key=True)

    character     = C(SmallInt, nullable=True)
    perks_0       = C(SmallInt, nullable=True)
    perks_1       = C(SmallInt, nullable=True)
    perks_2       = C(SmallInt, nullable=True)
    perks_3       = C(SmallInt, nullable=True)
    item          = C(SmallInt, nullable=True)
    addons_0      = C(SmallInt, nullable=True)
    addons_1      = C(SmallInt, nullable=True)
    offering      = C(SmallInt, nullable=True)
    status        = C(SmallInt, nullable=True)
    points        = C(Int, nullable=True)
    date_modified = C(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=text("now()"),
    )
    user_id          = C(SmallInt, FK(f"{TN.USER}.id"), nullable=True)
    extr_id          = C(SmallInt, FK(f"{TN.EXTRACTOR}.id"), nullable=True)
    user             = rel("User")
    extractor        = rel("Extractor")
    perks_mckd       = C(Bool, nullable=True)
    character_mckd   = C(Bool, nullable=True)
    item_mckd        = C(Bool, nullable=True)
    addons_mckd      = C(Bool, nullable=True)
    offering_mckd    = C(Bool, nullable=True)
    status_mckd      = C(Bool, nullable=True)
    points_mckd      = C(Bool, nullable=True)
    prestige         = C(SmallInt, nullable=True)
    prestige_mckd    = C(Bool, nullable=True)
