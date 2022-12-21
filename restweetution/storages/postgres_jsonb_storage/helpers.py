from typing import List

from pydantic import BaseModel
from sqlalchemy import and_, or_, Table
from sqlalchemy.future import select


def res_to_dicts(res):
    return [dict(r) for r in res]


def find_fields(datas: List[BaseModel]):
    fields = set()
    for d in datas:
        fields.update(d.__fields_set__)
    return fields


def update_dict(stmt, datas: List[BaseModel]):
    fields = find_fields(datas)
    to_update = {f: getattr(stmt.excluded, f) for f in fields}
    return to_update


def select_builder(table: Table, p_keys: List[str], fields: List[str] = None):
    if not fields:
        stmt = select(table)
    else:
        for key in p_keys:
            if key not in fields:
                fields.append(key)
        stmt = select(*[getattr(table.c, f) for f in fields])
    return stmt


def where_builder(stmt, is_and=True, *args):
    filters = [arg[0].in_(arg[1]) for arg in args if arg[1]]
    if not filters:
        return stmt

    connect = and_ if is_and else or_
    return stmt.where(connect(*filters))
