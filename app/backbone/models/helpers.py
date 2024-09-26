"""SQLAlchemy model definitions for helpers."""

from sqlalchemy import Column as C
from sqlalchemy import Date
from sqlalchemy import Integer as Int
from sqlalchemy import String as Str

from backbone.database import Base
from backbone.options import TABLE_NAMES as TN


class DBDVersion(Base):
    """SQLAlchemy DBD version model."""
    __tablename__ = TN.DBD_VERSION

    id   = C(Int, nullable=False, primary_key=True)
    name = C(Str, nullable=False)

    release_date = C(Date, nullable=True)
    common_name  = C(Str,  nullable=True)
