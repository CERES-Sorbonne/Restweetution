from typing import List

from pydantic import BaseModel


def row_to_dict(res):
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
