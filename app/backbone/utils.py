from sqlalchemy import inspect


def object_as_dict(obj) -> dict:
    return {
        c.key: getattr(obj, c.key)
        for c in inspect(obj).mapper.column_attrs
    }
