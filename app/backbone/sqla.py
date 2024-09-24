"""SQLAlchemy related functions."""

from sqlalchemy import func, inspect
from typing import TYPE_CHECKING

from backbone.options import TABLE_NAMES as TN

if TYPE_CHECKING:
    from sqlalchemy import Column


def object_as_dict(obj) -> dict:
    """Convert a sqlalchemy object into a dict."""
    return {c.key: getattr(obj, c.key) for c in inspect(obj).mapper.column_attrs}


def filter_with_text(query, model, search_text: str):
    """Add a filter to a sqlalchemy query based on the filtered column.
    search_text must already be non-empty.
    """
    search_text = search_text.lower()

    if model.__tablename__ in TN.NAME_FILTERED_TABLENAMES:
        return query.filter(func.lower(model.name).contains(search_text))
    elif model.__tablename__ == TN.MATCHES:
        return query.filter(func.lower(model.filename).contains(search_text))
    else:
        raise NotImplementedError


def fill_cols(
    model,
    text: str,
    is_for_killer: bool | None,
    type_model,
):
    """Efficient filling of columns in the SQLAlchemy SELECT statement."""
    cols = []
    only_type_model = True

    if is_for_killer is not None:
        if type_model is not None:
            cols.append(type_model.is_for_killer)
        else:
            only_type_model = False
            cols.append(model.is_for_killer)

    if text != "":
        only_type_model = False
        if model.__tablename__ in TN.NAME_FILTERED_TABLENAMES:
            cols.append(model.name)
        elif model.__tablename__ == TN.MATCHES:
            cols.append(model.filename)
        else:
            raise NotImplementedError

    if not cols:
        cols = [model.id]
    elif only_type_model:
        cols = [model.id] + cols

    return cols



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
