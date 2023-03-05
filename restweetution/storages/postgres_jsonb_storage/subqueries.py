"""
SQL Statement builder functions.
We want to keep most of SQL logic in this file
"""
from typing import List

from sqlalchemy import func, join, cast, text
from sqlalchemy.dialects.postgresql import JSON, array
from sqlalchemy.future import select

from restweetution.models.storage.queries import CollectionQuery, TweetFilter
from restweetution.storages.postgres_jsonb_storage.utils import date_from_to, offset_limit, select_join_builder, \
    where_in_builder
from restweetution.storages.postgres_jsonb_storage.models import TWEET, RULE_MATCH


def media_keys_stmt(collection: CollectionQuery):
    media_keys = select(
        func.jsonb_array_elements_text(TWEET.c.attachments['media_keys']).label('media_key'),
    )
    media_keys = media_keys.select_from(join(RULE_MATCH, TWEET))
    if collection.rule_ids:
        media_keys = media_keys.filter(RULE_MATCH.c.rule_id.in_(collection.rule_ids))
    media_keys = date_from_to(media_keys, TWEET.c.created_at, collection.date_from, collection.date_to)
    media_keys = offset_limit(media_keys, collection.offset, collection.limit)
    media_keys = media_keys.group_by('media_key')
    media_keys = media_keys.subquery('media_keys')

    return media_keys


def media_keys_with_tweet_id_stmt(collection: CollectionQuery):
    media_keys = select(
        func.string_agg(TWEET.c.id, ',').label('tweet_ids'),
        func.jsonb_array_elements_text(TWEET.c.attachments['media_keys']).label('media_key'),
    )
    media_keys = media_keys.select_from(join(RULE_MATCH, TWEET))
    if collection.rule_ids:
        media_keys = media_keys.filter(RULE_MATCH.c.rule_id.in_(collection.rule_ids))
    media_keys = date_from_to(media_keys, TWEET.c.created_at, collection.date_from, collection.date_to)
    media_keys = offset_limit(media_keys, collection.offset, collection.limit)
    media_keys = media_keys.group_by('media_key')
    media_keys = media_keys.subquery('media_keys')

    return media_keys


def stmt_extended_tweets_query(query: CollectionQuery, filter_: TweetFilter, only_ids=False):
    if only_ids:
        stmt = select(
            TWEET.c.id,
            func.json_agg(func.to_json(text('collected_tweet.rule_id'))).label('rule_ids')
        )
    else:
        stmt = select(
            func.to_json(text('tweet.*')).label('tweet'),
            func.json_agg(func.to_json(text('collected_tweet.*'))).label('rule_match')
        )

    stmt = stmt.select_from(TWEET.join(RULE_MATCH))

    if query.rule_ids:
        stmt = where_in_builder(stmt, True, (RULE_MATCH.c.rule_id, query.rule_ids))

    if query.direct_hit and query.rule_ids:
        stmt = stmt.where(RULE_MATCH.c.direct_hit.is_(True))
    if filter_.media:
        stmt = stmt.where(func.jsonb_array_length(TWEET.c.attachments['media_keys']) > 0)

    stmt = date_from_to(stmt, TWEET.c.created_at, query.date_from, query.date_to)
    stmt = offset_limit(stmt, query.offset, query.limit)
    if query.order < 0:
        stmt = stmt.order_by(TWEET.c.created_at.desc())
    elif query.order > 0:
        stmt = stmt.order_by(TWEET.c.created_at.asc())
    stmt = stmt.group_by(TWEET.c.id)
    return stmt


def stmt_tweet_media_ids(media_keys: List[str]):
    table = (
        select(func.jsonb_array_elements_text(TWEET.c.attachments['media_keys']).label('media_key'), TWEET.c.id)
        .where(TWEET.c.attachments['media_keys'].has_any(array(tuple(media_keys))))
        .subquery('tweet_media_ids')
    )
    stmt = select(table.c.media_key, func.string_agg(table.c.id, ',').label('tweet_ids')).group_by(table.c.media_key)
    return stmt
