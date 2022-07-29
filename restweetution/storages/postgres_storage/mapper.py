from sqlalchemy.orm import load_only, subqueryload, properties, ColumnProperty, selectinload

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


fields_by_type = {
    models.Tweet: tweet_fields,
    models.User: user_fields,
    models.Media: media_fields,
    models.Place: place_fields,
    models.Poll: poll_fields,
    models.Rule: rule_fields
}
