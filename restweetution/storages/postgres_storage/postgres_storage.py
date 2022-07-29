from asyncio import Lock
from typing import List, Iterator, Callable

from sqlalchemy import delete, exists
from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, joinedload

from restweetution.errors import handle_storage_save_error
from restweetution.models.bulk_data import BulkData
from restweetution.models.storage.custom_data import CustomData
from restweetution.models.storage.error import ErrorModel
from restweetution.models.twitter import Media, User, Poll, Place
from restweetution.models.twitter.rule import StreamRule
from restweetution.models.twitter.tweet import RestTweet
from restweetution.storages.storage import Storage
from . import models
from .mapper import set_query_params, fields_by_type
from ..query_params import tweet_fields, user_fields, poll_fields, place_fields, media_fields, rule_fields
from ...models import twitter


class PostgresStorage(Storage):
    def __init__(self, name: str, **kwargs):
        """
        Storage for postgres
        :param name: Name of the storage. Human friendly identifier
        :param url: Connection string
        """
        super().__init__(name=name, **kwargs)

        self._engine = create_async_engine(
            kwargs.get('url'),
            echo=False,
        )
        self._async_session = sessionmaker(
            self._engine, expire_on_commit=False, class_=AsyncSession
        )

        self.lock = Lock()

    async def save_error(self, error: ErrorModel):
        async with self._async_session() as session:
            pg_error = models.Error()
            pg_error.update(error.dict())
            session.add(pg_error)
            await session.commit()

    @handle_storage_save_error()
    async def save_bulk(self, data: BulkData):
        async with self.lock:
            async with self._async_session() as session:
                await self._save_tweets(session, data.get_tweets())
                await self._save_users(session, data.get_users())
                await self._save_place(session, data.get_places())
                await self._save_media(session, data.get_medias())
                await self._save_polls(session, data.get_polls())
                await self._save_rules(session, data.get_rules())

                # print(f'Postgres saved: {len(data.tweets.items())} tweets, {len(data.users.items())} users')
                await session.commit()
        #  emit event outside of lock !!
        await self._emit_save_event(bulk_data=data)

    async def save_custom_datas(self, datas: List[CustomData]):
        async with self._async_session() as session:
            for data in datas:
                pg_data = models.CustomData()
                pg_data.update(data.dict())
                await session.merge(pg_data)
            await session.commit()

    async def _save_tweets(self, session, tweets: List[RestTweet]):
        return await self._save_helper(session, models.Tweet, tweets)

    async def _save_users(self, session, users: List[User]):
        return await self._save_helper(session, models.User, users)

    async def _save_place(self, session, places: List[Place]):
        return await self._save_helper(session, models.Place, places)

    async def _save_polls(self, session, polls: List[Poll]):
        return await self._save_helper(session, models.Poll, polls)

    async def _save_media(self, session, medias: List[RestTweet]):
        return await self._save_helper(session, models.Media, medias, id_lambda=lambda x: x.media_key)

    # async def _save_tweets(self, session, tweets: List[RestTweet]):
    #     return await self._save_helper(session, self._get_tweets, models.Tweet, tweets)

    # get functions
    async def get_tweets(self,
                         ids: List[str] = None,
                         no_ids: List[str] = None,
                         fields: List[str] = tweet_fields
                         ) -> List[RestTweet]:
        async with self._async_session() as session:
            res = await self._get_helper(session, models.Tweet, ids, no_ids, fields)
            return [RestTweet(**r.to_dict()) for r in res]

    async def exist_tweets(self, ids: List[str] = None, no_ids: List[str] = None) -> List[str]:
        res = await self.get_tweets(ids=ids, no_ids=no_ids, fields=['id'])
        return [r.id for r in res]

    async def get_users(self,
                        ids: List[str] = None,
                        no_ids: List[str] = None,
                        fields: List[str] = user_fields) -> Iterator[User]:
        async with self._async_session() as session:
            res = await self._get_helper(session, models.User, ids, no_ids, fields)
            return [User(**r.to_dict()) for r in res]

    async def get_polls(self,
                        ids: List[str] = None,
                        no_ids: List[str] = None,
                        fields: List[str] = poll_fields) -> Iterator[Poll]:
        async with self._async_session() as session:
            res = await self._get_helper(session, models.Poll, ids, no_ids, fields)
            return [Poll(**r.to_dict()) for r in res]

    async def get_places(self,
                         ids: List[str] = None,
                         no_ids: List[str] = None,
                         fields: List[str] = place_fields) -> Iterator[Place]:
        async with self._async_session() as session:
            res = await self._get_helper(session, models.Place, ids, no_ids, fields)
            return [Place(**r.to_dict()) for r in res]

    async def get_medias(self,
                         ids: List[str] = None,
                         no_ids: List[str] = None,
                         fields: List[str] = media_fields) -> Iterator[Media]:
        async with self._async_session() as session:
            res = await self._get_helper(session, models.Media, ids, no_ids, fields, id_lambda=lambda x: x.media_key)
            return [Media(**r.to_dict()) for r in res]

    @staticmethod
    async def _media_exist(session, media_key: str):
        res = await session.execute(exists(select().where(models.Media.media_key == media_key)).select())
        exist = res.scalar()
        return exist

    async def get_rules(self,
                        ids: List[str] = None,
                        no_ids: List[str] = None,
                        fields: List[str] = rule_fields) -> List[StreamRule]:
        async with self._async_session() as session:
            fields = fields.copy()
            if 'tweet_ids' in fields:
                fields.remove('tweets_ids')
                fields.append('tweets')

            res = await self._get_helper(session, models.Rule, ids, no_ids, fields)
            res = [StreamRule(**r.to_dict()) for r in res]
            return res

    async def get_errors(self, ids: List[str] = None, no_ids: List[str] = None) -> List[ErrorModel]:
        async with self._async_session() as session:
            stmt = select(models.Error)
            if ids:
                stmt = stmt.filter(models.Error.id.in_(ids))
            if no_ids:
                stmt = stmt.filter(models.Tweet.id.notin_(no_ids))
            stmt = stmt.options(joinedload('*'))
            res = await session.execute(stmt)
            res = res.unique().scalars().all()
            res = [ErrorModel(**r.to_dict()) for r in res]
            return res

    async def get_custom_datas(self, key: str) -> List[CustomData]:
        async with self._async_session() as session:
            stmt = select(models.CustomData).filter_by(key=key)
            res = await session.execute(stmt)
            res = res.unique().scalars().all()
            res = [CustomData(**r.to_dict()) for r in res]
            return res

    # Delete functions
    async def del_custom_data(self, key: str, ids: List[str] = None):
        async with self._async_session() as session:
            stmt = delete(models.CustomData).filter(models.CustomData.key == key)
            if ids:
                stmt = stmt.filter(models.CustomData.id.in_(ids))
            await session.execute(stmt)
            await session.commit()

    # private utils

    @staticmethod
    async def _save_rules(session: any, rules: List[StreamRule]):
        for rule in rules:
            pg_rule = await session.get(models.Rule, rule.id)
            if not pg_rule:
                pg_rule = models.Rule()
                pg_rule.update(rule.dict())
                await session.merge(pg_rule)
            else:
                for tweet_id in rule.tweet_ids:
                    pg_collected = models.CollectedTweet()
                    pg_collected.update({'_parent_id': rule.id, 'tweet_id': tweet_id})
                    await session.merge(pg_collected)

    @staticmethod
    async def _get_helper(session,
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

    @staticmethod
    async def _save_helper(session, model, datas: list, id_lambda=lambda x: x.id):
        if not datas:
            return
        ids = [id_lambda(t) for t in datas]

        to_update = await PostgresStorage._get_helper(session, model, ids=ids, id_lambda=id_lambda)
        cache = {id_lambda(t): t for t in to_update}

        session.expunge_all()

        for data in datas:
            if id_lambda(data) in cache:
                pg_data = cache[id_lambda(data)]
                pg_data.update(data.dict(), ignore_empty=False)
            else:
                pg_data = model()
                pg_data.update(data.dict())
            await session.merge(pg_data)
