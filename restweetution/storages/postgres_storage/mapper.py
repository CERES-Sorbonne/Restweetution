from sqlalchemy.orm import load_only, subqueryload, properties, ColumnProperty, selectinload

from restweetution.storages.postgres_storage import models


def set_query_params(stmt, fields):
    cols = []
    rels = []
    for field in fields:
        pg_field = getattr(models.Tweet, field)
        if isinstance(pg_field.property, ColumnProperty):
            cols.append(pg_field)
        else:
            rels.append(pg_field)
    stmt = stmt.options(load_only(*cols))
    stmt = stmt.options(*[subqueryload(r) for r in rels])
    return stmt
