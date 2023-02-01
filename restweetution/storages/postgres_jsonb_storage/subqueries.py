"""
SQL Statement builder functions.
We want to keep most of SQL logic in this file
"""

from sqlalchemy import func, join
from sqlalchemy.future import select

from restweetution.models.storage.queries import CollectionQuery
from restweetution.storages.postgres_jsonb_storage.utils import date_from_to, offset_limit
from restweetution.storages.postgres_jsonb_storage.models import TWEET, COLLECTED_TWEET


def media_keys_stmt(collection: CollectionQuery):
    media_keys = select(
        func.jsonb_array_elements_text(TWEET.c.attachments['media_keys']).label('media_key'),
    )
    media_keys = media_keys.select_from(join(COLLECTED_TWEET, TWEET))
    if collection.rule_ids:
        media_keys = media_keys.filter(COLLECTED_TWEET.c.rule_id.in_(collection.rule_ids))
    media_keys = date_from_to(media_keys, TWEET.c.created_at, collection.date_from, collection.date_to)
    media_keys = offset_limit(media_keys, collection.offset, collection.limit)
    media_keys = media_keys.group_by('media_key')
    media_keys = media_keys.subquery('media_keys')

    return media_keys
