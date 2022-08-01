from typing import List, Callable, Tuple, Set

from sqlalchemy import select, cast, DECIMAL, BigInteger
from sqlalchemy.orm import load_only, subqueryload, ColumnProperty

from restweetution.storages.postgres_storage import models
from restweetution.storages.query_params import tweet_fields, user_fields, media_fields, place_fields, poll_fields, \
    rule_fields


def build_select(model, fields):
    stmt = select(model)
    cols = []
    rels = []
    for field in fields:
        pg_field = getattr(model, field)
        if isinstance(pg_field.property, ColumnProperty):
            cols.append(pg_field)
        else:
            rels.append(pg_field)
    stmt = stmt.options(load_only(*cols))
    stmt = stmt.options(*[subqueryload(r) for r in rels])
    return stmt


def set_order(stmt, model, sort_by: str, order: str = None):
    if not sort_by:
        return stmt
    sort_attr = getattr(model, sort_by)
    sort_attr = cast(sort_attr, BigInteger) if sort_by == 'id' else sort_attr
    sort_attr = sort_attr.desc() if order == 'desc' else sort_attr.asc()
    return stmt.order_by(sort_attr)


def set_filter(stmt, model, ids, no_ids, id_field, **kwargs):
    def _(key: str):
        return getattr(model, key)

    def _int(key: str):
        return cast(_(key), BigInteger)

    date_field = 'created_at'
    if 'date_field' in kwargs:
        date_field = kwargs.get('date_field')

    if ids:
        stmt = stmt.filter(_(id_field).in_(ids))
    if no_ids:
        stmt = stmt.filter(_(id_field).notin_(no_ids))
    if 'id_start' in kwargs:
        stmt = stmt.filter(_int(id_field) >= int(kwargs.get('id_start')))
    if 'id_stop' in kwargs:
        stmt = stmt.filter(_int(id_field) <= int(kwargs.get('id_stop')))
    if 'date_start' in kwargs:
        stmt = stmt.filter(_(date_field) >= kwargs.get('date_start'))
    if 'date_stop' in kwargs:
        stmt = stmt.filter(_(date_field) <= kwargs.get('date_stop'))
    # print(stmt)
    return stmt


async def get_helper(session,
                     pg_model,
                     ids: List[str] = None,
                     no_ids: List[str] = None,
                     fields: List[str] = None,
                     sort_by: str = None,
                     order: str = None,
                     id_field: str = 'id',
                     **kwargs):
    if fields is None:
        fields = fields_by_type[pg_model]

    stmt = build_select(pg_model, fields=fields)
    stmt = set_filter(stmt, pg_model, ids=ids, no_ids=no_ids, id_field=id_field, **kwargs)
    stmt = set_order(stmt, pg_model, sort_by, order)
    res = await session.execute(stmt)
    res = res.unique().scalars().all()
    return res


async def get_helper_without_session(conn,
                                     pg_model,
                                     ids: List[str] = None,
                                     no_ids: List[str] = None,
                                     fields: List[str] = None,
                                     sort_by: str = None,
                                     order: str = None,
                                     id_field: str = 'id',
                                     **kwargs):
    if fields is None:
        fields = fields_by_type[pg_model]

    stmt = build_select(pg_model, fields=fields)
    stmt = set_filter(stmt, pg_model, ids=ids, no_ids=no_ids, id_field=id_field, **kwargs)
    stmt = set_order(stmt, pg_model, sort_by, order)
    res = await conn.execute(stmt)
    res = res.unique().scalars().all()
    return res


async def save_helper(session, model, datas: list, id_field='id') -> Tuple[Set[str], Set[str]]:
    if not datas:
        return set(), set()

    def id_(x):
        return getattr(x, id_field)

    ids = [id_(t) for t in datas]

    to_update = await get_helper(session, model, ids=ids, id_field=id_field)
    cache = {id_(t): t for t in to_update}

    session.expunge_all()
    added = set()
    updated = set()

    for data in datas:
        if id_(data) in cache:
            pg_data = cache[id_(data)]
            pg_data.update(data.dict(), ignore_empty=True)
            updated.add(id_(data))
        else:
            pg_data = model()
            pg_data.update(data.dict())
            added.add(id_(data))
        await session.merge(pg_data)
    return added, updated


fields_by_type = {
    models.Tweet: tweet_fields,
    models.User: user_fields,
    models.Media: media_fields,
    models.Place: place_fields,
    models.Poll: poll_fields,
    models.Rule: rule_fields
}
