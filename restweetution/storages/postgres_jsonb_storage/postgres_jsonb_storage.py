import asyncio
import datetime
import logging
from typing import List, TypeVar, Callable, Dict

from pydantic import BaseModel
from sqlalchemy import update, bindparam, Table, delete, join, func
from sqlalchemy.dialects.postgresql import insert, array
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.future import select

from restweetution.models.bulk_data import BulkData
from restweetution.models.config.user_config import UserConfig
from restweetution.models.rule import Rule, CollectedTweet
from restweetution.models.storage.custom_data import CustomData
from restweetution.models.storage.downloaded_media import DownloadedMedia
from restweetution.models.storage.error import ErrorModel
from restweetution.models.twitter import Tweet, Media, User, Poll, Place
from restweetution.storages.postgres_jsonb_storage.helpers import res_to_dicts, update_dict, where_in_builder, \
    select_builder, primary_keys, offset_limit, date_from_to
from restweetution.storages.postgres_jsonb_storage.models import RULE, ERROR, meta_data, RESTWEET_USER, TWEET, MEDIA, \
    USER, POLL, PLACE, COLLECTED_TWEET, DOWNLOADED_MEDIA
from restweetution.storages.postgres_jsonb_storage.models.data import DATA
from restweetution.storages.system_storage import SystemStorage
from restweetution.utils import clean_dict, safe_dict

STORAGE_TYPE = 'postgres'
logger = logging.getLogger('PostgresJSONBStorage')


class PostgresJSONBStorage(SystemStorage):

    def __init__(self, url: str, name: str = None):
        if not name:
            name = STORAGE_TYPE
        super().__init__(name)

        self._engine = create_async_engine(url, echo=False)

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

    async def get_custom_datas(self, key: str) -> List[CustomData]:
        async with self._engine.begin() as conn:
            stmt = select(DATA).where(DATA.c.key == key)
            res = await conn.execute(stmt)
            res = res_to_dicts(res)
            res = [CustomData(**r) for r in res]
            return res

    async def get_rules_tweet_count(self):
        async with self._engine.begin() as conn:
            stmt = select(RULE, func.count(COLLECTED_TWEET.c.tweet_id).label('tweet_count')).select_from(
                join(RULE, COLLECTED_TWEET, isouter=True))
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
                await self._upsert_table(conn, TWEET, data.get_tweets())
            if data.medias:
                await self._upsert_table(conn, MEDIA, data.get_medias())
            if data.medias:
                await self._upsert_table(conn, USER, data.get_users())
            if data.polls:
                await self._upsert_table(conn, POLL, data.get_polls())
            if data.places:
                await self._upsert_table(conn, PLACE, data.get_places())

            if data.rules:
                await self._save_collected_refs(conn, data.get_rules())

            if callback:
                asyncio.create_task(callback(data))

    @staticmethod
    async def _save_collected_refs(conn, rules: List[Rule]):
        direct_hits = []
        includes = []
        for r in rules:
            coll = r.collected_tweets_list()
            for c in coll:
                if c.direct_hit:
                    direct_hits.append(c)
                else:
                    includes.append(c)
        if direct_hits:
            stmt = insert(COLLECTED_TWEET)
            stmt = stmt.on_conflict_do_update(
                index_elements=primary_keys(COLLECTED_TWEET),
                set_=dict(direct_hit=stmt.excluded.direct_hit)
            )
            values = [r.dict() for r in direct_hits]
            await conn.execute(stmt, values)
        if includes:
            stmt = insert(COLLECTED_TWEET)
            stmt = stmt.on_conflict_do_nothing(index_elements=primary_keys(COLLECTED_TWEET))
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
                stmt = stmt.select_from(join(TWEET, COLLECTED_TWEET))
                stmt = stmt.where(COLLECTED_TWEET.c.rule_id.in_(rule_ids))

            stmt = where_in_builder(stmt, True, (TWEET.c.id, ids))
            stmt = date_from_to(stmt, TWEET.c.created_at, date_from, date_to)
            stmt = offset_limit(stmt, offset, limit)
            if desc:
                stmt = stmt.order_by(TWEET.c.created_at.desc())
            else:
                stmt = stmt.order_by(TWEET.c.created_at.asc())
            res = await conn.execute(stmt)
            res = res_to_dicts(res)
            return res

    async def get_tweets_count(self,
                               date_from: datetime.datetime = None,
                               date_to: datetime.datetime = None,
                               rule_ids: List[int] = None) -> List[Dict]:
        async with self._engine.begin() as conn:
            stmt = select(func.count().label('count'))
            if rule_ids:
                stmt = stmt.select_from(join(TWEET, COLLECTED_TWEET))
                stmt = stmt.where(COLLECTED_TWEET.c.rule_id.in_(rule_ids))
            else:
                stmt = stmt.select_from(TWEET)
            stmt = date_from_to(stmt, TWEET.c.created_at, date_from, date_to)
            res = await conn.execute(stmt)
            res = res_to_dicts(res)
            res = res[0]['count']
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
            stmt = select(COLLECTED_TWEET)
            stmt = where_in_builder(stmt,
                                    is_and,
                                    (COLLECTED_TWEET.c.rule_id, ids),
                                    (COLLECTED_TWEET.c.tweet_id, tweet_ids))
            res = await conn.execute(stmt)
            res = res_to_dicts(res)
            collected = [CollectedTweet(**r) for r in res]

            rule_ids = {c.rule_id for c in collected}
            rules = await self.get_rules(ids=list(rule_ids))
            rule_dict: Dict[int, Rule] = {r.id: r for r in rules}

            for c in collected:
                rule_dict[c.rule_id].collected_tweets[c.tweet_id] = c

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
