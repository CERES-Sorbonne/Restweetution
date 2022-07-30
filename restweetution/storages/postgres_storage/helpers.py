from typing import List, Callable

from sqlalchemy import select
from sqlalchemy.orm import load_only, subqueryload, ColumnProperty

from restweetution.storages.postgres_storage import models
from restweetution.storages.query_params import tweet_fields, user_fields, media_fields, place_fields, poll_fields, \
    rule_fields


def set_query_params(stmt, model, fields):
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


async def get_helper(session,
                     pg_model,
                     ids: List[str] = None,
                     no_ids: List[str] = None,
                     fields: List[str] = None,
                     id_lambda: Callable = lambda x: x.id):
    if fields is None:
        fields = fields_by_type[pg_model]

    stmt = select(pg_model)

    if ids:
        stmt = stmt.filter(id_lambda(pg_model).in_(ids))
    if no_ids:
        stmt = stmt.filter(id_lambda(pg_model).notin_(no_ids))

    stmt = set_query_params(stmt, pg_model, fields)
    res = await session.execute(stmt)
    res = res.unique().scalars().all()
    return res


async def save_helper(session, model, datas: list, id_lambda=lambda x: x.id):
    if not datas:
        return [], []
    ids = [id_lambda(t) for t in datas]

    to_update = await get_helper(session, model, ids=ids, id_lambda=id_lambda)
    cache = {id_lambda(t): t for t in to_update}

    session.expunge_all()
    added = []
    updated = []

    for data in datas:
        if id_lambda(data) in cache:
            pg_data = cache[id_lambda(data)]
            pg_data.update(data.dict(), ignore_empty=True)
            updated.append(data)
        else:
            pg_data = model()
            pg_data.update(data.dict())
            added.append(data)
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
