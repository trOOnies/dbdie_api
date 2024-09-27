"""SQLAlchemy related functions."""

from sqlalchemy import func, inspect, or_
from typing import TYPE_CHECKING

from backbone.options import TABLE_NAMES as TN

if TYPE_CHECKING:
    from sqlalchemy import Column
    from sqlalchemy.orm import Query, Session


def soft_bool_filter(col, cond: bool):
    """Leave bool values equal to 'cond' AND the null bool values."""
    return or_(col.is_(cond), col.is_(None))


def join_and_filter_ifk(query: "Query", model, model_type, ifk: bool) -> "Query":
    if (model_type is not None) and (ifk is not None):
        query = query.join(model_type)
        if model.__tablename__ in {TN.OFFERING, TN.PERKS, TN.STATUS}:
            query = query.filter(soft_bool_filter(model_type.is_killer, ifk))
        else:
            query = query.filter(soft_bool_filter(model_type.is_for_killer, ifk))
    elif model.__tablename__ == TN.CHARACTER:
        query = query.filter(soft_bool_filter(model.is_killer, ifk))

    return query


def limit_and_skip(query: "Query", limit: int, skip: int) -> "Query":
    return (
        query.limit(limit)
        if skip == 0
        else query.limit(limit).offset(skip)
    )


def filter_with_text(query: "Query", model, search_text: str) -> "Query":
    """Add a filter to a sqlalchemy query based on the filtered column.
    search_text must already be non-empty.
    """
    if search_text == "":
        return query

    search_text = search_text.lower()

    if model.__tablename__ in TN.NAME_FILTERED_TABLENAMES:
        return query.filter(func.lower(model.name).contains(search_text))
    elif model.__tablename__ == TN.MATCHES:
        return query.filter(func.lower(model.filename).contains(search_text))
    else:
        raise NotImplementedError


def get_items_query(
    db: "Session",
    limit: int,
    model,
    skip: int,
    ifk: bool | None,
    model_type,
    text: str,
) -> "Query":
    """Base get many function. 'model' is the sqlalchemy model."""
    assert limit > 0
    assert skip >= 0

    query = db.query(model)
    query = join_and_filter_ifk(query, model, model_type, ifk)
    query = filter_with_text(query, model, text)
    query = limit_and_skip(query, limit, skip)
    return query


def object_as_dict(obj) -> dict:
    """Convert a sqlalchemy object into a dict."""
    return {c.key: getattr(obj, c.key) for c in inspect(obj).mapper.column_attrs}


def fill_cols_custom(
    options: list[tuple["Column", bool | None]],
    default_cols: list["Column"],
    force_prepend_default_col: bool,
) -> list["Column"]:
    """Efficient custom filling of columns in the SQLAlchemy SELECT statement."""
    cols = [c for c, v in options if v is not None]
    if not cols:
        cols = default_cols
    elif force_prepend_default_col:
        cols = default_cols + cols
    return cols
