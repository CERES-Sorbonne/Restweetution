from asyncio import Lock
from typing import List, Iterator

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import sessionmaker, joinedload

from restweetution.errors import handle_storage_save_error
from restweetution.models import twitter
from restweetution.models.bulk_data import BulkData
from restweetution.models.error import ErrorModel
from restweetution.models.stream_rule import StreamRule
from restweetution.models.twitter.tweet import RestTweet
from restweetution.storage.storages.storage import Storage
from restweetution.storage.storages.postgres_storage.models import User, Place, Rule, Error
from restweetution.storage.storages.postgres_storage.models.media import Media
from restweetution.storage.storages.postgres_storage.models.poll import Poll
from restweetution.storage.storages.postgres_storage.models.rule import CollectedTweet
from restweetution.storage.storages.postgres_storage.models.tweet import Tweet


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
            pg_error = Error()
            pg_error.update(error.dict())
            session.add(pg_error)
            await session.commit()

    @handle_storage_save_error()
    async def save_bulk(self, data: BulkData):
        async with self.lock:
            async with self._async_session() as session:
                for key in data.tweets:
                    pg_tweet = Tweet()
                    pg_tweet.update(data.tweets[key].dict())
                    await session.merge(pg_tweet)
                for key in data.users:
                    pg_user = User()
                    pg_user.update(data.users[key].dict())
                    await session.merge(pg_user)
                for key in data.places:
                    pg_place = Place()
                    pg_place.update(data.places[key].dict())
                    await session.merge(pg_place)
                for key in data.medias:
                    pg_media = Media()
                    pg_media.update(data.medias[key].dict())
                    await session.merge(pg_media)
                for key in data.polls:
                    pg_poll = Poll()
                    pg_poll.update(data.polls[key].dict())
                    await session.merge(pg_poll)
                for key in data.rules:
                    await self._add_or_update_rule(session, data.rules[key])

                await session.commit()
                await self._emit_save_event(bulk_data=data)
                # print(f'Postgres saved: {len(data.tweets.items())} tweets, {len(data.users.items())} users')

    # Update functions
    async def update_medias(self, medias: List[Media]):
        async with self._async_session() as session:
            db_medias = await self._get_medias(session, ids=[m.media_key for m in medias])
            for media, db_media in zip(medias, db_medias):
                db_media.update(media.dict())
                await session.merge(db_media)
            await session.commit()

    # get functions
    async def get_tweets(self, ids: List[str] = None, no_ids: List[str] = None) -> List[RestTweet]:
        async with self._async_session() as session:
            stmt = select(Tweet)
            if ids:
                stmt = stmt.filter(Tweet.id.in_(ids))
            if no_ids:
                stmt = stmt.filter(Tweet.id.notin_(no_ids))
            stmt = stmt.options(joinedload('*'))
            res = await session.execute(stmt)
            res = res.unique().scalars().all()
            res = [RestTweet(**r.to_dict()) for r in res]
            return res

    async def get_users(self, ids: List[str] = None, no_ids: List[str] = None) -> Iterator[User]:
        async with self._async_session() as session:
            stmt = select(User)
            if ids:
                stmt = stmt.filter(User.id.in_(ids))
            if no_ids:
                stmt = stmt.filter(User.id.notin_(no_ids))
            stmt = stmt.options(joinedload('*'))
            res = await session.execute(stmt)
            res = res.unique().scalars().all()
            res = [twitter.User(**r.to_dict()) for r in res]
            return res

    async def get_polls(self, ids: List[str] = None, no_ids: List[str] = None) -> Iterator[Poll]:
        async with self._async_session() as session:
            stmt = select(Poll)
            if ids:
                stmt = stmt.filter(Poll.id.in_(ids))
            if no_ids:
                stmt = stmt.filter(Poll.id.notin_(no_ids))
            stmt = stmt.options(joinedload('*'))
            res = await session.execute(stmt)
            res = res.unique().scalars().all()
            res = [twitter.Poll(**r.to_dict()) for r in res]
            return res

    async def get_places(self, ids: List[str] = None, no_ids: List[str] = None) -> Iterator[Place]:
        async with self._async_session() as session:
            stmt = select(Place)
            if ids:
                stmt = stmt.filter(Place.id.in_(ids))
            if no_ids:
                stmt = stmt.filter(Place.id.notin_(no_ids))
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
    async def _get_medias(session, ids: List[str] = None, no_ids: List[str] = None) -> List[Media]:
        stmt = select(Media)
        if ids:
            stmt = stmt.filter(Media.media_key.in_(ids))
        if no_ids:
            stmt = stmt.filter(Media.media_key.notin_(no_ids))
        stmt = stmt.options(joinedload('*'))
        res = await session.execute(stmt)
        res = res.unique().scalars().all()
        return res

    async def get_rules(self, ids: List[str] = None, no_ids: List[str] = None) -> List[StreamRule]:
        async with self._async_session() as session:
            stmt = select(Rule)
            if ids:
                stmt = stmt.filter(Rule.id.in_(ids))
            if no_ids:
                stmt = stmt.filter(Tweet.id.notin_(no_ids))
            stmt = stmt.options(joinedload('*'))
            res = await session.execute(stmt)
            res = res.unique().scalars().all()
            res = [twitter.StreamRule(**r.to_dict()) for r in res]
            return res

    async def get_errors(self, ids: List[str] = None, no_ids: List[str] = None) -> List[ErrorModel]:
        async with self._async_session() as session:
            stmt = select(Error)
            if ids:
                stmt = stmt.filter(Error.id.in_(ids))
            if no_ids:
                stmt = stmt.filter(Tweet.id.notin_(no_ids))
            stmt = stmt.options(joinedload('*'))
            res = await session.execute(stmt)
            res = res.unique().scalars().all()
            res = [ErrorModel(**r.to_dict()) for r in res]
            return res
    # private utils

    @staticmethod
    async def _add_or_update_rule(session: any, rule):
        pg_rule = await session.get(Rule, rule.id)
        if not pg_rule:
            pg_rule = Rule()
            pg_rule.update(rule.dict())
            await session.merge(pg_rule)
        else:
            for tweet_id in rule.tweet_ids:
                pg_collected = CollectedTweet()
                pg_collected.update({'_parent_id': rule.id, 'tweet_id': tweet_id})
                await session.merge(pg_collected)
