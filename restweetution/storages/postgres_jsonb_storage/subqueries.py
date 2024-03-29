"""
SQL Statement builder functions.
We want to keep most of SQL logic in this file
"""
from typing import List

from sqlalchemy import func, join, text, distinct
from sqlalchemy.dialects.postgresql import array
from sqlalchemy.future import select

from restweetution.models.storage.queries import CollectionQuery, TweetFilter
from restweetution.storages.postgres_jsonb_storage.models import TWEET, RULE_MATCH, MEDIA
from restweetution.storages.postgres_jsonb_storage.utils import date_from_to, offset_limit, where_in_builder


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


def stmt_query_tweets(query: CollectionQuery, filter_: TweetFilter):
    stmt = select(
        func.to_json(text('tweet.*')).label('tweet'),
        func.json_agg(func.to_json(text('collected_tweet.*'))).label('rule_match')
    )

    stmt = stmt.select_from(TWEET.join(RULE_MATCH))

    stmt = where_in_builder(stmt, True, (RULE_MATCH.c.rule_id, query.rule_ids), (TWEET.c.id, query.tweet_ids))

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


def stmt_query_tweets_sample(query: CollectionQuery):

    stmt_matches = select(RULE_MATCH)
    stmt_matches = where_in_builder(stmt_matches, True, (RULE_MATCH.c.rule_id, query.rule_ids))
    # stmt_matches = date_from_to(stmt_matches, TWEET.c.created_at, query.date_from, query.date_to)
    if query.direct_hit and query.rule_ids:
        stmt_matches = stmt_matches.where(RULE_MATCH.c.direct_hit.is_(True))
    stmt_matches = offset_limit(stmt_matches, query.offset, query.limit)
    matches = stmt_matches.alias('matches')

    stmt = select(
        func.to_json(text('tweet.*')).label('tweet'),
        func.json_agg(func.to_json(text('matches.*'))).label('rule_match')
    )

    stmt = stmt.select_from(TWEET.join(matches, matches.c.tweet_id == TWEET.c.id))
    stmt = stmt.group_by(TWEET.c.id)
    return stmt


def stmt_get_rule_matches(rule_ids: List[int]):
    stmt = select(RULE_MATCH)
    if rule_ids:
        stmt = where_in_builder(stmt, False, (RULE_MATCH.c.rule_id, rule_ids))
    return stmt


def stmt_query_medias(query: CollectionQuery, filter_: TweetFilter):
    media_tweet = select(
        TWEET.c.id.label('tweet_id'),
        func.jsonb_array_elements_text(TWEET.c.attachments['media_keys']).label('media_key')
    )

    media_tweet = media_tweet.select_from(TWEET.join(RULE_MATCH, isouter=True))

    if query.rule_ids:
        media_tweet = where_in_builder(media_tweet, True, (RULE_MATCH.c.rule_id, query.rule_ids))

    if query.direct_hit and query.rule_ids:
        media_tweet = media_tweet.where(RULE_MATCH.c.direct_hit.is_(True))
    if filter_.media:
        media_tweet = media_tweet.where(func.jsonb_array_length(TWEET.c.attachments['media_keys']) > 0)

    media_tweet = date_from_to(media_tweet, TWEET.c.created_at, query.date_from, query.date_to)
    if query.order < 0:
        media_tweet = media_tweet.order_by(TWEET.c.created_at.desc())
    elif query.order > 0:
        media_tweet = media_tweet.order_by(TWEET.c.created_at.asc())

    media_tweet = media_tweet.alias('media_tweet')

    media_to_tweets = select(media_tweet.c.media_key, func.json_agg(media_tweet.c.tweet_id).label('tweet_ids'))
    media_to_tweets = media_to_tweets.group_by(media_tweet.c.media_key)
    media_to_tweets = media_to_tweets.alias('media_to_tweets')

    medias = select(
        # MEDIA.c.media_key,
        func.to_json(text('media.*')).label('media'),
        media_to_tweets.c.tweet_ids
    )
    medias = medias.select_from(media_to_tweets.join(MEDIA, media_to_tweets.c.media_key == MEDIA.c.media_key))
    medias = offset_limit(medias, query.offset, query.limit)

    return medias


def stmt_query_count_medias(query: CollectionQuery, filter_: TweetFilter):
    media_tweet = select(
        TWEET.c.id.label('tweet_id'),
        func.jsonb_array_elements_text(TWEET.c.attachments['media_keys']).label('media_key')
    )

    media_tweet = media_tweet.select_from(TWEET.join(RULE_MATCH, isouter=True))

    if query.rule_ids:
        media_tweet = where_in_builder(media_tweet, True, (RULE_MATCH.c.rule_id, query.rule_ids))

    if query.direct_hit and query.rule_ids:
        media_tweet = media_tweet.where(RULE_MATCH.c.direct_hit.is_(True))
    if filter_.media:
        media_tweet = media_tweet.where(func.jsonb_array_length(TWEET.c.attachments['media_keys']) > 0)

    media_tweet = date_from_to(media_tweet, TWEET.c.created_at, query.date_from, query.date_to)
    media_tweet = media_tweet.alias('media_tweet')

    media_to_tweets = select(media_tweet.c.media_key, func.json_agg(media_tweet.c.tweet_id).label('tweet_ids'))
    media_to_tweets = media_to_tweets.group_by(media_tweet.c.media_key)
    media_to_tweets = media_to_tweets.alias('media_to_tweets')

    medias = select(
        func.count(MEDIA.c.media_key).label('count')
    )
    medias = medias.select_from(media_to_tweets.join(MEDIA, media_to_tweets.c.media_key == MEDIA.c.media_key))
    return medias


def stmt_query_count_tweets(query: CollectionQuery, filter_: TweetFilter):
    stmt = select(func.count().label('count'))
    if query.rule_ids and len(query.rule_ids) > 1:
        stmt = select(func.count(distinct(TWEET.c.id)).label('count'))

    if query.rule_ids:
        stmt = stmt.select_from(TWEET.join(RULE_MATCH))
    else:
        stmt = stmt.select_from(TWEET)

    if query.rule_ids:
        stmt = where_in_builder(stmt, True, (RULE_MATCH.c.rule_id, query.rule_ids))
        if query.direct_hit and query.rule_ids:
            stmt = stmt.where(RULE_MATCH.c.direct_hit.is_(True))

    if filter_.media:
        stmt = stmt.where(func.jsonb_array_length(TWEET.c.attachments['media_keys']) > 0)

    stmt = date_from_to(stmt, TWEET.c.created_at, query.date_from, query.date_to)

    return stmt


def stmt_tweet_media_ids(media_keys: List[str]):
    table = (
        select(func.jsonb_array_elements_text(TWEET.c.attachments['media_keys']).label('media_key'), TWEET.c.id)
        .where(TWEET.c.attachments['media_keys'].has_any(array(tuple(media_keys))))
        .subquery('tweet_media_ids')
    )
    stmt = select(table.c.media_key, func.string_agg(table.c.id, ',').label('tweet_ids')).group_by(table.c.media_key)
    return stmt
