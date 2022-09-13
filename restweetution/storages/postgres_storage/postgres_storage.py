from asyncio import Lock
from typing import List, Iterator, Tuple, Set

from sqlalchemy import delete, cast, BigInteger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, joinedload

from restweetution.errors import handle_storage_save_error
from restweetution.models.bulk_data import BulkData
from restweetution.models.event_data import EventData
from restweetution.models.storage.custom_data import CustomData
from restweetution.models.storage.error import ErrorModel
from restweetution.models.twitter import Media, User, Poll, Place
from restweetution.models.rule import StreamAPIRule, Rule
from restweetution.models.twitter.tweet import Tweet
from restweetution.storages.storage import Storage
from . import models
from .helpers import get_helper, save_helper, get_statement, request_history_update
from .models import TweetPublicMetricsHistory, Base
from ..query_params import tweet_fields, user_fields, poll_fields, place_fields, media_fields, rule_fields


class PostgresStorage(Storage):

    def __init__(self, name: str, url: str, **kwargs):
        """
        Storage for postgres
        :param name: Name of the storage. Human friendly identifier
        :param url: Connection string
        """
        super().__init__(name=name, **kwargs)

        self._engine = create_async_engine(
            url,
            echo=False,
        )
        self._async_session = sessionmaker(
            self._engine, expire_on_commit=False, class_=AsyncSession
        )
        self._history = True
        self.lock = Lock()

        async with self._engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    def get_engine(self):
        return self._engine

    async def get_tweet_ids(self):
        async with self._engine.begin() as conn:
            stmt = get_statement(models.Tweet, fields=['id'])
            res = await conn.execute(stmt)
            res = res.scalars().all()
            return res

    async def update_error(self):
        async with self._async_session() as session:
            stmt = select(models.CollectedTweet).order_by(
                cast(models.CollectedTweet.tweet_id, BigInteger).desc()).limit(1)
            res = await session.execute(stmt)
            print(res.scalars().all()[0].tweet_id)
            return res

    @handle_storage_save_error()
    async def save_bulk(self, data: BulkData):
        async with self.lock:
            async with self._async_session() as session:
                t_add, t_up = await self._save_tweets(session, data.get_tweets())
                u_add, u_up = await self._save_users(session, data.get_users())
                pl_add, pl_up = await self._save_place(session, data.get_places())
                m_add, m_up = await self._save_media(session, data.get_medias())
                po_add, po_up = await self._save_polls(session, data.get_polls())
                r_add, r_up = await self._save_rules(session, data.get_rules())

                # print(f'Postgres saved: {len(data.tweets.items())} tweets, {len(data.users.items())} users')
                if self._history:
                    await self._save_history(session, bulk_data=data)

                await session.commit()

        # Events outside of lock !!

        event_data = EventData(data=data)
        event_data.added.add(tweets=t_add, users=u_add, places=pl_add, medias=m_add, polls=po_add, rules=r_add)
        event_data.updated.add(tweets=t_up, users=u_up, places=pl_up, medias=m_up, polls=po_up, rules=r_up)

        await self.save_event(event_data)
        await self.update_event(event_data)

    async def save_custom_datas(self, datas: List[CustomData]):
        async with self._async_session() as session:
            for data in datas:
                pg_data = models.CustomData()
                pg_data.update(data.dict())
                pg_res = await session.merge(pg_data)
                print(pg_res.id)
            await session.commit()

    async def save_error(self, error: ErrorModel):
        async with self._async_session() as session:
            pg_error = models.Error()
            pg_error.update(error.dict())
            session.add(pg_error)
            await session.commit()

    # get functions
    async def get_tweets(self,
                         ids: List[str] = None,
                         no_ids: List[str] = None,
                         fields: List[str] = tweet_fields,
                         sort_by: str = None,
                         order: str = None,
                         **kwargs) -> List[Tweet]:
        async with self._async_session() as session:
            res = await get_helper(session, models.Tweet, ids=ids, no_ids=no_ids, fields=fields, sort_by=sort_by,
                                   order=order, **kwargs)
            return [Tweet(**r.to_dict()) for r in res]

    async def get_users(self,
                        ids: List[str] = None,
                        no_ids: List[str] = None,
                        fields: List[str] = user_fields) -> Iterator[User]:
        async with self._async_session() as session:
            res = await get_helper(session, models.User, ids=ids, no_ids=no_ids, fields=fields)
            return [User(**r.to_dict()) for r in res]

    async def get_polls(self,
                        ids: List[str] = None,
                        no_ids: List[str] = None,
                        fields: List[str] = poll_fields) -> Iterator[Poll]:
        async with self._async_session() as session:
            res = await get_helper(session, models.Poll, ids=ids, no_ids=no_ids, fields=fields)
            return [Poll(**r.to_dict()) for r in res]

    async def get_places(self,
                         ids: List[str] = None,
                         no_ids: List[str] = None,
                         fields: List[str] = place_fields) -> Iterator[Place]:
        async with self._async_session() as session:
            res = await get_helper(session, models.Place, ids=ids, no_ids=no_ids, fields=fields)
            return [Place(**r.to_dict()) for r in res]

    async def get_medias(self,
                         ids: List[str] = None,
                         no_ids: List[str] = None,
                         fields: List[str] = media_fields) -> Iterator[Media]:
        async with self._async_session() as session:
            res = await get_helper(session, models.Media, ids=ids, no_ids=no_ids, fields=fields, id_field='media_key')
            return [Media(**r.to_dict()) for r in res]

    async def get_rules(
            self,
            ids: List[str] = None,
            no_ids: List[str] = None,
            fields: List[str] = rule_fields) -> List[StreamAPIRule]:
        async with self._async_session() as session:
            fields = fields.copy()
            if 'tweet_ids' in fields:
                fields.remove('tweet_ids')
                fields.append('tweets')

            res = await get_helper(session, models.Rule, ids=ids, no_ids=no_ids, fields=fields)
            res = [StreamAPIRule(**r.to_dict()) for r in res]
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

    async def del_custom_datas(self, key: str, ids: List[str] = None):
        async with self._async_session() as session:
            stmt = delete(models.CustomData).filter(models.CustomData.key == key)
            if ids:
                stmt = stmt.filter(models.CustomData.id.in_(ids))
            await session.execute(stmt)
            await session.commit()

    # private utils

    @staticmethod
    async def _save_tweets(session, tweets: List[Tweet]):
        return await save_helper(session, models.Tweet, tweets)

    @staticmethod
    async def _save_users(session, users: List[User]):
        return await save_helper(session, models.User, users)

    @staticmethod
    async def _save_place(session, places: List[Place]):
        return await save_helper(session, models.Place, places)

    @staticmethod
    async def _save_polls(session, polls: List[Poll]):
        return await save_helper(session, models.Poll, polls)

    @staticmethod
    async def _save_media(session, medias: List[Tweet]):
        return await save_helper(session, models.Media, medias, id_field='media_key')

    @staticmethod
    async def _save_rules(session: any, rules: List[Rule]) -> Tuple[Set[int], Set[int]]:
        added = set()
        updated = set()
        for rule in rules:
            # print(rule)
            for tweet_id in rule.tweet_ids:
                # print(type(tweet_id))
                pg_collected = models.CollectedTweet()
                pg_collected.update({'_parent_id': rule.id, 'tweet_id': tweet_id})
                await session.merge(pg_collected)
                updated.add(rule.id)
        return added, updated

    @staticmethod
    async def _get_rule(session, rule: Rule):
        stmt = select(models.Rule).filter(models.Rule.tag == rule.tag).filter(models.Rule.query == rule.query)
        stmt = stmt.filter(models.Rule.name == rule.name).filter(models.Rule.type == rule.type)
        res = await session.execute(stmt)
        res = res.scalars().first()
        return res

    async def request_rules(self, rules: List[Rule]):
        async with self._async_session() as session:
            for rule in rules:
                pg_rule = await self._get_rule(session, rule)
                if not pg_rule:
                    pg_rule = models.Rule()
                    pg_rule.update(rule.dict())
                    pg_rule = await session.merge(pg_rule)
                await session.commit()
                rule.id = pg_rule.id
        return rules

    @staticmethod
    def should_save(value):
        return True

    @staticmethod
    async def _save_history(session, bulk_data: BulkData):
        if not bulk_data.timestamp:
            return

        for tweet in bulk_data.get_tweets():
            if tweet.public_metrics:
                await PostgresStorage._save_history_helper(session, TweetPublicMetricsHistory, tweet.id,
                                                           tweet.public_metrics.dict(), bulk_data.timestamp)

    @staticmethod
    async def _save_history_helper(session, pg_model, parent_id, data, timestamp):
        if not request_history_update(pg_model, parent_id, data, timestamp):
            return
        pg_history = pg_model()
        pg_history.update(data)
        pg_history.timestamp = timestamp
        pg_history.parent_id = parent_id
        await session.merge(pg_history)
