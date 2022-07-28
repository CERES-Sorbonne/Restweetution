from asyncio import Lock
from typing import List, Iterator

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
from .mapper import set_query_params
from ..query_params import tweet_fields
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
                for key in data.tweets:
                    pg_tweet = models.Tweet()
                    pg_tweet.update(data.tweets[key].dict())
                    await session.merge(pg_tweet)
                for key in data.users:
                    pg_user = models.User()
                    pg_user.update(data.users[key].dict())
                    await session.merge(pg_user)
                for key in data.places:
                    pg_place = models.Place()
                    pg_place.update(data.places[key].dict())
                    await session.merge(pg_place)
                for key in data.medias:
                    if await self._media_exist(session, data.medias[key].media_key):
                        continue
                    pg_media = models.Media()
                    pg_media.update(data.medias[key].dict())
                    await session.merge(pg_media)
                for key in data.polls:
                    pg_poll = models.Poll()
                    pg_poll.update(data.polls[key].dict())
                    await session.merge(pg_poll)
                for key in data.rules:
                    await self._add_or_update_rule(session, data.rules[key])
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

    # Update functions
    async def update_medias(self, medias: List[Media]):
        async with self.lock:
            async with self._async_session() as session:
                db_medias = await self._get_medias(session, ids=[m.media_key for m in medias])
                for media, db_media in zip(medias, db_medias):
                    db_media.update(media.dict())
                    await session.merge(db_media)
                await session.commit()
        await self.update_event(medias=medias)

    # get functions
    async def get_tweets(self,
                         ids: List[str] = None,
                         no_ids: List[str] = None,
                         fields: List[str] = tweet_fields
                         ) -> List[RestTweet]:
        async with self._async_session() as session:

            stmt = select(models.Tweet)
            if ids:
                stmt = stmt.filter(models.Tweet.id.in_(ids))
            if no_ids:
                stmt = stmt.filter(models.Tweet.id.notin_(no_ids))

            stmt = set_query_params(stmt, fields)
            res = await session.execute(stmt)
            res = res.unique().scalars().all()
            res = [RestTweet(**r.to_dict()) for r in res]
            return res

    async def get_users(self, ids: List[str] = None, no_ids: List[str] = None) -> Iterator[User]:
        async with self._async_session() as session:
            stmt = select(models.User)
            if ids:
                stmt = stmt.filter(models.User.id.in_(ids))
            if no_ids:
                stmt = stmt.filter(models.User.id.notin_(no_ids))
            stmt = stmt.options(joinedload('*'))
            res = await session.execute(stmt)
            res = res.unique().scalars().all()
            res = [twitter.User(**r.to_dict()) for r in res]
            return res

    async def get_polls(self, ids: List[str] = None, no_ids: List[str] = None) -> Iterator[Poll]:
        async with self._async_session() as session:
            stmt = select(models.Poll)
            if ids:
                stmt = stmt.filter(models.Poll.id.in_(ids))
            if no_ids:
                stmt = stmt.filter(models.Poll.id.notin_(no_ids))
            stmt = stmt.options(joinedload('*'))
            res = await session.execute(stmt)
            res = res.unique().scalars().all()
            res = [twitter.Poll(**r.to_dict()) for r in res]
            return res

    async def get_places(self, ids: List[str] = None, no_ids: List[str] = None) -> Iterator[Place]:
        async with self._async_session() as session:
            stmt = select(models.Place)
            if ids:
                stmt = stmt.filter(models.Place.id.in_(ids))
            if no_ids:
                stmt = stmt.filter(models.Place.id.notin_(no_ids))
            stmt = stmt.options(joinedload('*'))
            res = await session.execute(stmt)
            res = res.unique().scalars().all()
            res = [twitter.Place(**r.to_dict()) for r in res]
            return res

    async def get_medias(self, ids: List[str] = None, no_ids: List[str] = None) -> List[twitter.Media]:
        async with self._async_session() as session:
            res = await self._get_medias(session, ids=ids, no_ids=no_ids)
            res = [twitter.Media(**r.to_dict()) for r in res]
            return res

    @staticmethod
    async def _media_exist(session, media_key: str):
        res = await session.execute(exists(select().where(models.Media.media_key == media_key)).select())
        exist = res.scalar()
        return exist

    @staticmethod
    async def _get_medias(session, ids: List[str] = None, no_ids: List[str] = None) -> List[models.Media]:
        stmt = select(models.Media)
        if ids:
            stmt = stmt.filter(models.Media.media_key.in_(ids))
        if no_ids:
            stmt = stmt.filter(models.Media.media_key.notin_(no_ids))
        stmt = stmt.options(joinedload('*'))
        res = await session.execute(stmt)
        res = res.unique().scalars().all()
        return res

    async def get_rules(self, ids: List[str] = None, no_ids: List[str] = None) -> List[StreamRule]:
        async with self._async_session() as session:
            stmt = select(models.Rule)
            if ids:
                stmt = stmt.filter(models.Rule.id.in_(ids))
            if no_ids:
                stmt = stmt.filter(models.Tweet.id.notin_(no_ids))
            stmt = stmt.options(joinedload('*'))
            res = await session.execute(stmt)
            res = res.unique().scalars().all()
            res = [twitter.StreamRule(**r.to_dict()) for r in res]
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
            res = await session.execute(stmt)
            await session.commit()

    # private utils

    @staticmethod
    async def _add_or_update_rule(session: any, rule):
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
