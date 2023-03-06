import asyncio
import datetime
import logging
import time
from typing import List, TypeVar, Callable, Dict

from pydantic import BaseModel
from sqlalchemy import update, bindparam, Table, delete, join, func, true
from sqlalchemy.dialects.postgresql import insert, array
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.future import select

from restweetution.models.bulk_data import BulkData
from restweetution.models.config.user_config import UserConfig
from restweetution.models.extended_types import ExtendedMedia, ExtendedTweet
from restweetution.models.linked.linked_bulk_data import LinkedBulkData
from restweetution.models.rule import Rule, RuleMatch
from restweetution.models.storage.custom_data import CustomData
from restweetution.models.storage.downloaded_media import DownloadedMedia
from restweetution.models.storage.error import ErrorModel
from restweetution.models.storage.queries import CollectionQuery, TweetFilter
from restweetution.models.twitter import Tweet, Media, User, Poll, Place
from restweetution.storages.postgres_jsonb_storage.models import RULE, ERROR, meta_data, RESTWEET_USER, TWEET, MEDIA, \
    USER, POLL, PLACE, RULE_MATCH, DOWNLOADED_MEDIA
from restweetution.storages.postgres_jsonb_storage.models.data import DATA
from restweetution.storages.postgres_jsonb_storage.subqueries import media_keys_stmt, media_keys_with_tweet_id_stmt, \
    stmt_query_count_tweets, stmt_tweet_media_ids, stmt_query_tweets, stmt_query_medias, stmt_query_count_medias
from restweetution.storages.postgres_jsonb_storage.utils import res_to_dicts, update_dict, where_in_builder, \
    select_builder, primary_keys, offset_limit, date_from_to, select_join_builder
from restweetution.storages.system_storage import SystemStorage
from restweetution.utils import clean_dict, safe_dict

STORAGE_TYPE = 'postgres'
logger = logging.getLogger('PostgresJSONBStorage')


class PostgresJSONBStorage(SystemStorage):

    def __init__(self, url: str, name: str = None):
        if not name:
            name = STORAGE_TYPE
        super().__init__(name)

        self._url = url
        self._engine = create_async_engine(url, echo=False)

    def get_engine(self):
        return self._engine

    async def reset_database(self):
        async with self._engine.begin() as conn:
            await conn.run_sync(meta_data.drop_all)
            await conn.run_sync(meta_data.create_all)

    async def build_tables(self):
        async with self._engine.begin() as conn:
            await conn.run_sync(meta_data.create_all)

    TRule = TypeVar('TRule', bound=Rule)

    async def request_rules(self, rules: List[TRule], override=False) -> List[TRule]:

        async with self._engine.begin() as conn:
            stmt = insert(RULE)
            to_update = dict(created_at=RULE.c.created_at)
            if override:
                to_update['tag'] = stmt.excluded.tag

            stmt = stmt.on_conflict_do_update(index_elements=['query'], set_=to_update)
            stmt = stmt.returning(RULE.c.id)
            values = [clean_dict(r.dict()) for r in rules]
            await conn.execute(stmt, values)

            stmt = select(RULE).where(RULE.c.query.in_([r.query for r in rules]))
            res = await conn.execute(stmt)
            res = res_to_dicts(res)
            res = [Rule(**r) for r in res]
            query_to_rule = {r.query: r for r in res}

            for r in rules:
                r.id = query_to_rule[r.query].id

            return rules

    async def save_error(self, error: ErrorModel):
        async with self._engine.begin() as conn:
            stmt = insert(ERROR)
            values = clean_dict(error.dict())
            await conn.execute(stmt, values)

    async def save_restweet_users(self, restweet_users: List[UserConfig]):
        async with self._engine.begin() as conn:
            stmt = insert(RESTWEET_USER)
            values = [safe_dict(user.dict()) for user in restweet_users]
            await conn.execute(stmt, values)

    async def rm_restweet_users(self, user_ids: List[str]):
        async with self._engine.begin() as conn:
            stmt = delete(RESTWEET_USER).where(RESTWEET_USER.c.name.in_(user_ids))
            await conn.execute(stmt)

    async def update_restweet_user(self, restweet_users: List[UserConfig]):
        async with self._engine.begin() as conn:
            stmt = update(RESTWEET_USER).where(RESTWEET_USER.c.name == bindparam('name_key'))

            values = [dict(
                name_key=user.name,
                searcher_state=safe_dict(user.searcher_state.dict()),
                streamer_state=safe_dict(user.streamer_state.dict())
            ) for user in restweet_users]

            await conn.execute(stmt, values)

    async def get_restweet_users(self) -> List[UserConfig]:
        async with self._engine.begin() as conn:
            stmt = select(RESTWEET_USER)
            res = await conn.execute(stmt)
            res = res_to_dicts(res)
            res = [UserConfig(**r) for r in res]
            return res

    async def get_token(self, config_name: str):
        async with self._engine.begin() as conn:
            stmt = (
                select(RESTWEET_USER.c.bearer_token)
                .where(RESTWEET_USER.c.name == config_name)
            )
            res = await conn.execute(stmt)
            res = res_to_dicts(res)
            res = [r['bearer_token'] for r in res]
            return res[0]

    async def get_custom_datas(self, key: str) -> List[CustomData]:
        async with self._engine.begin() as conn:
            stmt = select(DATA).where(DATA.c.key == key)
            res = await conn.execute(stmt)
            res = res_to_dicts(res)
            res = [CustomData(**r) for r in res]
            return res

    async def get_rules_tweet_count(self):
        async with self._engine.begin() as conn:
            stmt = select(RULE, func.count(RULE_MATCH.c.tweet_id).label('tweet_count')).select_from(
                join(RULE, RULE_MATCH, isouter=True))
            stmt = stmt.group_by(RULE.c.id)
            res = await conn.execute(stmt)
            res = res_to_dicts(res)
            return res

    async def del_custom_datas(self, key: str):
        pass

    async def save_custom_datas(self, datas: List[CustomData]):
        async with self._engine.begin() as conn:
            stmt = insert(DATA)
            stmt = stmt.on_conflict_do_update(index_elements=['id', 'key'], set_=dict(stmt.excluded))
            values = [dict(id=d.id, key=d.key, data=safe_dict(d.data)) for d in datas]

            await conn.execute(stmt, values)

    async def save_downloaded_medias(self, downloaded_medias: List[DownloadedMedia]):
        async with self._engine.begin() as conn:
            await self._save_downloaded_medias(conn, downloaded_medias)

    @staticmethod
    async def _save_downloaded_medias(conn, downloaded_medias: List[DownloadedMedia]):
        stmt = insert(DOWNLOADED_MEDIA)
        stmt = stmt.on_conflict_do_update(index_elements=['media_key'], set_=dict(stmt.excluded))
        values = [d.dict() for d in downloaded_medias]

        await conn.execute(stmt, values)

    async def get_downloaded_medias(self,
                                    media_keys: List[str] = None,
                                    urls: List[str] = None,
                                    is_and=True,
                                    full=False):

        async with self._engine.begin() as conn:
            selected = [MEDIA, DOWNLOADED_MEDIA] if full else [DOWNLOADED_MEDIA]
            stmt = select(*selected)
            if full or urls:
                stmt = stmt.select_from(join(MEDIA, DOWNLOADED_MEDIA))

            stmt = where_in_builder(stmt, is_and, (MEDIA.c.url, urls), (DOWNLOADED_MEDIA.c.media_key, media_keys))

            res = await conn.execute(stmt)
            res = res_to_dicts(res)
            if full:
                res = [DownloadedMedia(**r, media=Media(**r)) for r in res]
            else:
                res = [DownloadedMedia(**r) for r in res]
            return res

    async def save_bulk(self, data: BulkData, callback: Callable = None):
        async with self._engine.begin() as conn:

            if data.tweets:
                old = time.time()
                await self._upsert_table(conn, TWEET, data.get_tweets())
                logger.debug(f'save tweet: {time.time() - old}')
            if data.medias:
                old = time.time()
                await self._upsert_table(conn, MEDIA, data.get_medias())
                logger.debug(f'save media: {time.time() - old}')
            if data.users:
                old = time.time()
                await self._upsert_table(conn, USER, data.get_users())
                logger.debug(f'save users: {time.time() - old}')
            if data.polls:
                old = time.time()
                await self._upsert_table(conn, POLL, data.get_polls())
                logger.debug(f'save polls: {time.time() - old}')
            if data.places:
                # old = time.time()
                await self._upsert_table(conn, PLACE, data.get_places())
                logger.debug(f'save places: {time.time() - old}')

            matches = data.get_rule_matches()
            if matches:
                await self._save_rule_match(conn, matches)
            # if data.downloaded_medias:
            #     await self._save_downloaded_medias(conn, data.get_downloaded_medias())

            if callback:
                asyncio.create_task(callback(data))

    @staticmethod
    async def _save_rule_match(conn, matches: List[RuleMatch]):
        direct_hits = []
        includes = []
        for match in matches:
            if match.direct_hit:
                direct_hits.append(match)
            else:
                includes.append(match)
        if direct_hits:
            stmt = insert(RULE_MATCH)
            stmt = stmt.on_conflict_do_update(
                index_elements=primary_keys(RULE_MATCH),
                set_=dict(direct_hit=stmt.excluded.direct_hit)
            )
            values = [r.dict() for r in direct_hits]
            await conn.execute(stmt, values)
        if includes:
            stmt = insert(RULE_MATCH)
            stmt = stmt.on_conflict_do_nothing(index_elements=primary_keys(RULE_MATCH))
            values = [r.dict() for r in includes]
            await conn.execute(stmt, values)

    @staticmethod
    async def _upsert_table(conn, table: Table, rows: List[BaseModel]):
        stmt = insert(table)
        stmt = stmt.on_conflict_do_update(
            index_elements=primary_keys(table),
            set_=update_dict(stmt, rows)
        )
        values = [r.dict() for r in rows]
        await conn.execute(stmt, values)

    async def get_tweets(self,
                         fields: List[str] = None,
                         ids: List[str] = None,
                         date_from: datetime.datetime = None,
                         date_to: datetime.datetime = None,
                         offset: int = None,
                         limit: int = None,
                         rule_ids: List[int] = None,
                         direct_hit: bool = False,
                         desc: bool = False) -> List[Tweet]:
        res = await self.get_tweets_raw(fields=fields,
                                        ids=ids,
                                        date_from=date_from,
                                        date_to=date_to,
                                        offset=offset,
                                        limit=limit,
                                        rule_ids=rule_ids,
                                        desc=desc)
        res = [Tweet(**r) for r in res]
        return res

    async def get_tweets_raw(self,
                             fields: List[str] = None,
                             ids: List[str] = None,
                             date_from: datetime.datetime = None,
                             date_to: datetime.datetime = None,
                             offset: int = None,
                             limit: int = None,
                             rule_ids: List[int] = None,
                             desc: bool = False) -> List[Dict]:
        async with self._engine.begin() as conn:
            stmt = select_builder(TWEET, ['id'], fields)

            if rule_ids:
                stmt = stmt.select_from(join(TWEET, RULE_MATCH))
                stmt = stmt.where(RULE_MATCH.c.rule_id.in_(rule_ids))

            stmt = where_in_builder(stmt, True, (TWEET.c.id, ids))
            stmt = date_from_to(stmt, TWEET.c.created_at, date_from, date_to)
            stmt = offset_limit(stmt, offset, limit)
            if desc:
                stmt = stmt.order_by(TWEET.c.created_at.order())
            else:
                stmt = stmt.order_by(TWEET.c.created_at.asc())
            res = await conn.execute(stmt)
            res = res_to_dicts(res)
            return res

    @staticmethod
    def _get_collected_tweets_stmt(tweet_fields: List[str] = None,
                                   collected_fields: List[str] = None,
                                   ids: List[str] = None,
                                   date_from: datetime.datetime = None,
                                   date_to: datetime.datetime = None,
                                   rule_ids: List[int] = None,
                                   direct_hit: bool = False,
                                   order: int = 0,
                                   offset: int = None,
                                   limit: int = None):
        stmt = select_join_builder((TWEET, tweet_fields), (RULE_MATCH, collected_fields))

        stmt = where_in_builder(stmt, True, (TWEET.c.id, ids), (RULE_MATCH.c.rule_id, rule_ids))
        if direct_hit:
            stmt = stmt.where(RULE_MATCH.c.direct_hit)

        stmt = date_from_to(stmt, TWEET.c.created_at, date_from, date_to)
        stmt = offset_limit(stmt, offset, limit)
        if order < 0:
            stmt = stmt.order_by(TWEET.c.created_at.desc())
        elif order > 0:
            stmt = stmt.order_by(TWEET.c.created_at.asc())
        return stmt

    async def get_collected_tweets(self,
                                   tweet_fields: List[str] = None,
                                   collected_fields: List[str] = None,
                                   ids: List[str] = None,
                                   date_from: datetime.datetime = None,
                                   date_to: datetime.datetime = None,
                                   rule_ids: List[int] = None,
                                   direct_hit: bool = False,
                                   order: int = 0,
                                   offset: int = None,
                                   limit: int = None) -> List[RuleMatch]:
        async with self._engine.begin() as conn:
            stmt = self._get_collected_tweets_stmt(tweet_fields, collected_fields, ids, date_from, date_to, rule_ids,
                                                   direct_hit, order, offset, limit)
            res = await conn.execute(stmt)
            res = res_to_dicts(res)
            res = [RuleMatch(**r, tweet=Tweet(**r)) for r in res]
            return res

    async def get_collected_tweets_stream(self,
                                          tweet_fields: List[str] = None,
                                          collected_fields: List[str] = None,
                                          ids: List[str] = None,
                                          date_from: datetime.datetime = None,
                                          date_to: datetime.datetime = None,
                                          rule_ids: List[int] = None,
                                          direct_hit: bool = False,
                                          order: int = 0,
                                          offset: int = None,
                                          limit: int = None,
                                          chunk_size=1000):
        async with self._engine.begin() as conn:
            stmt = self._get_collected_tweets_stmt(tweet_fields, collected_fields, ids, date_from, date_to, rule_ids,
                                                   direct_hit, order, offset, limit)
            conn = await conn.execution_options(yield_per=chunk_size, stream_results=True)
            conn = await conn.stream(stmt)
            async for res in conn.partitions(chunk_size):
                res = res_to_dicts(res)
                collected = [RuleMatch(**r, tweet=Tweet(**r)) for r in res]
                yield collected

    async def get_tweets_count(self,
                               date_from: datetime.datetime = None,
                               date_to: datetime.datetime = None,
                               rule_ids: List[int] = None,
                               direct_hit: bool = False) -> int:
        async with self._engine.begin() as conn:
            stmt = select(func.count().label('count'))
            if rule_ids:
                stmt = stmt.select_from(join(TWEET, RULE_MATCH))
                stmt = stmt.where(RULE_MATCH.c.rule_id.in_(rule_ids))
                if direct_hit and rule_ids:
                    stmt = stmt.where(RULE_MATCH.c.direct_hit == true())
            else:
                stmt = stmt.select_from(TWEET)
            stmt = date_from_to(stmt, TWEET.c.created_at, date_from, date_to)
            res = await conn.execute(stmt)
            res = res_to_dicts(res)
            res = res[0]['count']
            return res

    async def get_rule_matches(self, tweet_ids: List[str], rule_ids: List[int]):
        async with self._engine.begin() as conn:
            stmt = select(RULE_MATCH)
            stmt = where_in_builder(stmt, (RULE_MATCH.c.tweet_id, tweet_ids), (RULE_MATCH.c.rule_id, rule_ids))
            res = await conn.execute(stmt)
            res = res_to_dicts(res)
            res = [RuleMatch(**r) for r in res]
            return res

    async def get_users(self, fields: List[str] = None, ids: List[str] = None) -> List[User]:
        res = await self.get_users_raw(fields=fields, ids=ids)
        res = [User(**r) for r in res]
        return res

    async def get_users_raw(self, fields: List[str] = None, ids: List[str] = None) -> List[Dict]:
        async with self._engine.begin() as conn:
            stmt = select_builder(USER, ['id'], fields)
            stmt = where_in_builder(stmt, True, (USER.c.id, ids))
            res = await conn.execute(stmt)
            res = res_to_dicts(res)
            return res

    async def get_tweets_with_media_keys(self, media_keys: List[str], fields: List[str] = None):
        async with self._engine.begin() as conn:
            stmt = select_builder(TWEET, ['id'], fields)
            stmt = stmt.where(TWEET.c.attachments['media_keys'].has_any(array(tuple(media_keys))))
            res = await conn.execute(stmt)
            res = res_to_dicts(res)
            res = [Tweet(**r) for r in res]
            return res

    async def get_medias(self, fields: List[str] = None, media_keys: List[str] = None) -> List[Media]:
        async with self._engine.begin() as conn:
            stmt = select_builder(MEDIA, ['media_key'], fields)
            stmt = where_in_builder(stmt, True, (MEDIA.c.media_key, media_keys))
            res = await conn.execute(stmt)
            res = res_to_dicts(res)
            res = [Media(**m) for m in res]
            return res

    async def get_media_keys_from_collection(self, collection: CollectionQuery) -> List[str]:
        async with self._engine.begin() as conn:
            stmt = media_keys_stmt(collection)
            res = await conn.execute(stmt)
            res = res_to_dicts(res)
            res = [r['media_key'] for r in res]
            return res

    async def get_medias_from_collection(self, collection: CollectionQuery):
        async with self._engine.begin() as conn:
            media_keys = media_keys_stmt(collection)
            stmt = select(MEDIA).select_from(join(media_keys, MEDIA, media_keys.c.media_key == MEDIA.c.media_key))

            res = await conn.execute(stmt)
            res = res_to_dicts(res)
            res = [Media(**r) for r in res]
            return res

    async def get_downloaded_medias_from_collection(self, collection: CollectionQuery, load_media=False):
        async with self._engine.begin() as conn:
            media_keys = media_keys_stmt(collection)
            if not load_media:
                stmt = select(DOWNLOADED_MEDIA).select_from(
                    join(media_keys, DOWNLOADED_MEDIA, media_keys.c.media_key == DOWNLOADED_MEDIA.c.media_key)
                )
            else:
                stmt = select(DOWNLOADED_MEDIA, MEDIA).select_from(
                    join(media_keys, DOWNLOADED_MEDIA, media_keys.c.media_key == DOWNLOADED_MEDIA.c.media_key)
                    .join(MEDIA, media_keys.c.media_key == MEDIA.c.media_key)
                )

            res = await conn.execute(stmt)
            res = res_to_dicts(res)
            if load_media:
                res = [DownloadedMedia(**r, media=Media(**r)) for r in res]
            else:
                res = [DownloadedMedia(**r) for r in res]
            return res

    async def get_extended_medias(self, media_keys: List[str], tweet_ids=False, downloaded=True):
        """
        Get Extended Media information from Storage by media_key
        @param media_keys: media_keys to retrieve
        @param tweet_ids: Default False, set True if you need to know which tweet has this media
        @param downloaded: Default True, load info about the corresponding downloaded media, if it exists
        @return: List of extended medias
        """
        async with self._engine.begin() as conn:
            if tweet_ids:
                tweet_media = stmt_tweet_media_ids(media_keys)
                media = (
                    select(MEDIA, tweet_media.c.tweet_ids)
                    .select_from(MEDIA.join(tweet_media, MEDIA.c.media_key == tweet_media.c.media_key))
                )
            else:
                media = select(MEDIA).where(MEDIA.c.media_key.in_(media_keys))

            if downloaded:
                media_sub = media.subquery('media_sub')
                media = (
                    select(media_sub, DOWNLOADED_MEDIA)
                    .select_from(media_sub.join(
                        DOWNLOADED_MEDIA, media_sub.c.media_key == DOWNLOADED_MEDIA.c.media_key, isouter=True)
                    )
                )

            res = await conn.execute(media)
            res = res_to_dicts(res)
            xmedias = []
            for r in res:
                t_ids = r['tweet_ids'].split(',') if tweet_ids else []
                d_media = DownloadedMedia(**r) if downloaded and r['sha1'] else None

                media = Media(**r)
                xmedias.append(ExtendedMedia(media=media, downloaded=d_media, tweet_ids=t_ids))
            return xmedias

    async def query_extended_medias(self, query: CollectionQuery):
        async with self._engine.begin() as conn:
            media_keys = media_keys_with_tweet_id_stmt(query)
            stmt = select(media_keys.c.tweet_ids, MEDIA).select_from(
                media_keys.join(MEDIA, media_keys.c.media_key == MEDIA.c.media_key))
            res = await conn.execute(stmt)
            res = res_to_dicts(res)
            res = [ExtendedMedia(media=Media(**r), tweet_ids=r['tweet_ids'].split(',')) for r in res]
            return res

    # async def query_xtweets(self, query: CollectionQuery, tweet_filter: TweetFilter = None):
    #     field_source = 'sources'
    #     async with self._engine.begin() as conn:
    #         if not tweet_filter:
    #             tweet_filter = TweetFilter()
    #         print(tweet_filter)
    #         stmt = stmt_query_count_tweets(query, tweet_filter)
    #         res = await conn.execute(stmt)
    #         res = res_to_dicts(res)
    #
    #         extended_tweets = []
    #         for r in res:
    #             xtweet = ExtendedTweet(tweet=Tweet(**r))
    #             if field_source in r:
    #                 xtweet.sources.extend([RuleMatch(**s) for s in r[field_source]])
    #             extended_tweets.append(xtweet)
    #
    #         return extended_tweets

    async def query_count_tweets(self, query: CollectionQuery, tweet_filter: TweetFilter = None):
        async with self._engine.begin() as conn:
            if not tweet_filter:
                tweet_filter = TweetFilter()

            stmt = stmt_query_count_tweets(query, tweet_filter)
            res = await conn.execute(stmt)
            res = res_to_dicts(res)
            return res[0]['count']

    async def query_count_medias(self, query: CollectionQuery, tweet_filter: TweetFilter = None):
        async with self._engine.begin() as conn:
            if not tweet_filter:
                tweet_filter = TweetFilter()

            stmt = stmt_query_count_medias(query, tweet_filter)
            res = await conn.execute(stmt)
            res = res_to_dicts(res)
            return res[0]['count']

    async def query_tweets(self, query: CollectionQuery, tweet_filter: TweetFilter = None):
        async with self._engine.begin() as conn:
            if not tweet_filter:
                tweet_filter = TweetFilter()

            stmt = stmt_query_tweets(query, tweet_filter)
            res = await conn.execute(stmt)
            res = res_to_dicts(res)

            tweets = [Tweet(**r['tweet']) for r in res]
            matches = [r['rule_match'] for r in res]
            rule_matches = []
            for m in matches:
                rule_matches.extend(m)
            rule_matches = [RuleMatch(**m) for m in rule_matches]

            res_data = LinkedBulkData()
            res_data.add_tweets(tweets)
            res_data.add_rule_matches(rule_matches)

            # linked_tweets = res_data.get_linked_tweets()

            return res_data

    async def get_tweets_stream(self, query: CollectionQuery, tweet_filter: TweetFilter = None, chunk_size=10):
        async with self._engine.begin() as conn:
            if not tweet_filter:
                tweet_filter = TweetFilter()

            stmt = stmt_query_tweets(query, tweet_filter)
            conn = await conn.stream(stmt)
            async for res in conn.partitions(chunk_size):
                res = res_to_dicts(res)

                tweets = [Tweet(**r['tweet']) for r in res]
                matches = [r['rule_match'] for r in res]
                rule_matches = []
                for m in matches:
                    rule_matches.extend(m)
                rule_matches = [RuleMatch(**m) for m in rule_matches]

                res_data = LinkedBulkData()
                res_data.add_tweets(tweets)
                res_data.add_rule_matches(rule_matches)

                yield res_data

    async def query_medias(self, query: CollectionQuery, downloaded=True):
        async with self._engine.begin() as conn:
            stmt = stmt_query_medias(query, TweetFilter(media=True))
            res = await conn.execute(stmt)
            res = res_to_dicts(res)

            media_to_tweets = {}
            medias = []
            for r in res:
                media = Media(**r['media'])
                medias.append(media)
                tweet_ids = r['tweet_ids']
                media_to_tweets[media.media_key] = set(tweet_ids)

            data = LinkedBulkData()
            data.media_to_tweets = media_to_tweets
            data.add_medias(medias)

            if downloaded:
                d_medias = await self.get_downloaded_medias(media_keys=[m.media_key for m in medias])
                data.add_downloaded_medias(d_medias)

            return data

    async def get_rules(self,
                        fields: List[str] = None,
                        ids: List[int] = None,
                        is_and=True) -> List[Rule]:
        async with self._engine.begin() as conn:
            stmt = select_builder(RULE, ['id'], fields)
            stmt = where_in_builder(stmt, is_and, (RULE.c.id, ids))
            res = await conn.execute(stmt)
            res = res_to_dicts(res)
            res = [Rule(**r) for r in res]
            return res

    async def get_rule_with_collected_tweets(self,
                                             tweet_ids: List[str] = None,
                                             ids: List[int] = None,
                                             is_and=True) -> List[Rule]:
        async with self._engine.begin() as conn:
            stmt = select(RULE_MATCH)
            stmt = where_in_builder(stmt,
                                    is_and,
                                    (RULE_MATCH.c.rule_id, ids),
                                    (RULE_MATCH.c.tweet_id, tweet_ids))
            res = await conn.execute(stmt)
            res = res_to_dicts(res)
            collected = [RuleMatch(**r) for r in res]

            rule_ids = {c.rule_id for c in collected}
            rules = await self.get_rules(ids=list(rule_ids))
            rule_dict: Dict[int, Rule] = {r.id: r for r in rules}

            for c in collected:
                rule_dict[c.rule_id].matches[c.tweet_id] = c

            return rules

    async def get_polls(self, fields: List[str] = None, ids: List[str] = None) -> List[Poll]:
        async with self._engine.begin() as conn:
            stmt = select_builder(POLL, ['id'], fields)
            stmt = where_in_builder(stmt, True, (POLL.c.id, ids))
            res = await conn.execute(stmt)
            res = res_to_dicts(res)
            res = [Poll(**p) for p in res]
            return res

    async def get_places(self, fields: List[str] = None, ids: List[str] = None) -> List[Place]:
        async with self._engine.begin() as conn:
            stmt = select_builder(PLACE, ['id'], fields)
            stmt = where_in_builder(stmt, True, (PLACE.c.id, ids))
            res = await conn.execute(stmt)
            res = res_to_dicts(res)
            res = [Place(**p) for p in res]
            return res
