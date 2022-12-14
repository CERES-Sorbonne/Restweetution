import logging
from itertools import chain
from typing import List

from pydantic import BaseModel
from sqlalchemy import update, bindparam, Table, delete, join, func
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.future import select

from restweetution.models.bulk_data import BulkData
from restweetution.models.config.user_config import UserConfig
from restweetution.models.rule import Rule
from restweetution.models.storage.custom_data import CustomData
from restweetution.models.storage.error import ErrorModel
from restweetution.models.twitter import Tweet
from restweetution.storages.postgres_jsonb_storage.helpers import row_to_dict, update_dict
from restweetution.storages.postgres_jsonb_storage.models import RULE, ERROR, meta_data, RESTWEET_USER, TWEET, MEDIA, \
    USER, POLL, PLACE, COLLECTED_TWEET
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

    async def request_rules(self, rules: List[Rule], override=False) -> List[Rule]:

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
            res = row_to_dict(res)
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
            res = row_to_dict(res)
            res = [UserConfig(**r) for r in res]
            return res

    async def get_custom_datas(self, key: str) -> List[CustomData]:
        async with self._engine.begin() as conn:
            stmt = select(DATA).where(DATA.c.key == key)
            res = await conn.execute(stmt)
            res = row_to_dict(res)
            res = [CustomData(**r) for r in res]
            return res

    async def get_rules_tweet_count(self):
        async with self._engine.begin() as conn:

            stmt = select(RULE, func.count(COLLECTED_TWEET.c.tweet_id).label('tweet_count')).select_from(join(COLLECTED_TWEET, RULE))
            stmt = stmt.group_by(RULE.c.id)
            res = await conn.execute(stmt)
            res = row_to_dict(res)
            return res

    async def del_custom_datas(self, key: str):
        pass

    async def save_custom_datas(self, datas: List[CustomData]):
        async with self._engine.begin() as conn:
            stmt = insert(DATA)
            stmt = stmt.on_conflict_do_update(index_elements=['id', 'key'], set_=dict(stmt.excluded))
            values = [dict(id=d.id, key=d.key, data=safe_dict(d.data)) for d in datas]

            await conn.execute(stmt, values)

    async def save_bulk(self, data: BulkData):
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
                rules = data.get_rules()
                collected = list(chain(*[r.collected_tweets.values() for r in rules]))
                if collected:
                    await self._upsert_table(conn, COLLECTED_TWEET, collected)




    @staticmethod
    async def _upsert_table(conn, table: Table, rows: List[BaseModel]):
        stmt = insert(table)
        stmt = stmt.on_conflict_do_update(
            index_elements=[k.name for k in table.primary_key],
            set_=update_dict(stmt, rows)
        )
        values = [r.dict() for r in rows]
        await conn.execute(stmt, values)

    async def get_tweets(self, fields: List[str] = None, **kwargs) -> List[Tweet]:
        async with self._engine.begin() as conn:
            if not fields:
                stmt = select(TWEET)
            else:
                if 'id' not in fields:
                    fields.append('id')
                stmt = select(*[getattr(TWEET.c, f) for f in fields])
            res = await conn.execute(stmt)
            res = row_to_dict(res)
            res = [Tweet(**r) for r in res]
            return res
