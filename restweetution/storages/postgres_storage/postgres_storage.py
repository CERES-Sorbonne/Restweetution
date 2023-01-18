import datetime
import logging
from asyncio import Lock
from typing import List, Iterator, Tuple, Set, Dict

from sqlalchemy import delete, cast, BigInteger, func, tuple_
from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, joinedload

from restweetution.errors import handle_storage_save_error
from restweetution.models.bulk_data import BulkData
from restweetution.models.event_data import EventData, BulkIds
from restweetution.models.rule import Rule, CollectedTweet
from restweetution.models.storage.custom_data import CustomData
from restweetution.models.storage.error import ErrorModel
from restweetution.models.twitter import Media, User, Poll, Place
from restweetution.models.twitter.tweet import Tweet
from restweetution.storages.storage import Storage
from . import models
from .helpers import get_helper, save_helper, get_statement, request_history_update, get_helper_stmt
from .models import TweetPublicMetricsHistory
from ..query_params import tweet_fields, user_fields, poll_fields, place_fields, media_fields, rule_fields
from ...models.config.user_config import UserConfig

STORAGE_TYPE = 'postgres'
logger = logging.getLogger('PostgresStorage')


class PostgresStorage(Storage):

    def __init__(self, url: str, name: str = 'postgres', **kwargs):
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
        self.url = url
        self.lock = Lock()

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
                cast(models.CollectedTweet.tweet_id, BigInteger).order()).limit(1)
            res = await session.execute(stmt)
            print(res.scalars().all()[0].tweet_id)
            return res

    def get_config(self):
        return {
            'type': STORAGE_TYPE,
            'name': self.name,
            'url': self.url
        }

    @handle_storage_save_error()
    async def save_bulk(self, data: BulkData):
        async with self.lock:
            async with self._async_session() as session:
                t_add, t_up = await self._save_tweets(session, data.get_tweets())
                u_add, u_up = await self._save_users(session, data.get_users())
                pl_add, pl_up = await self._save_place(session, data.get_places())
                m_add, m_up = await self._save_media(session, data.get_medias())
                po_add, po_up = await self._save_polls(session, data.get_polls())
                r_add, r_up = await self._update_rules(session, data.get_rules())

                logger.info(f'Postgres saved: {len(t_add)} tweets, updated: {len(t_up)}')
                if self._history:
                    await self._save_history(session, bulk_data=data)

                await session.commit()

        # Events outside of lock !!

        added_ids = BulkIds(tweets=t_add, users=u_add, places=pl_add, medias=m_add, polls=po_add, rules=r_add)
        updated_ids = BulkIds(tweets=t_up, users=u_up, places=pl_up, medias=m_up, polls=po_up, rules=r_up)

        event_data = EventData(data=data, added=added_ids, updated=updated_ids)

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

    async def save_user_configs(self, user_configs: List[UserConfig]):
        async with self._async_session() as session:
            for config in user_configs:
                pg_config = models.UserConfig()
                pg_config.update(config.dict())
                await session.merge(pg_config)
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

    async def get_tweets_stream(self):
        async with self._async_session() as conn:
            stmt = get_helper_stmt(pg_model=models.Tweet, fields=tweet_fields)
            stream = await conn.stream(stmt)

            async for res in stream.scalars():
                yield Tweet(**res.to_dict())

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
                         fields: List[str] = media_fields) -> List[Dict]:
        async with self._async_session() as session:
            res = await get_helper(session, models.Media, ids=ids, no_ids=no_ids, fields=fields, id_field='media_key')
            return [r.to_dict() for r in res]

    async def get_rules(
            self,
            ids: List[str] = None,
            no_ids: List[str] = None,
            fields: List[str] = rule_fields) -> List[Rule]:
        async with self._async_session() as session:
            fields = fields.copy()
            if 'tweet_ids' in fields:
                fields.remove('tweet_ids')
                fields.append('tweets')

            res = await get_helper(session, models.Rule, ids=ids, no_ids=no_ids, fields=fields)
            res = [Rule(**r.to_dict()) for r in res]
            return res

    async def get_rules_tweet_count(self, ids: List[int] = None) -> Dict[(int, int)]:
        """
        Returns a list of tuple ( rule_id, count) where count is the number of collected tweets for the given rule
        """
        async with self._async_session() as session:
            stmt = select(models.CollectedTweet.rule_id, func.count(models.CollectedTweet.rule_id))
            stmt = stmt.group_by(models.CollectedTweet.rule_id)
            if ids:
                stmt = stmt.filter(models.CollectedTweet.rule_id.in_(ids))

            res = await session.execute(stmt)
            res = res.all()
            return {r[0]: r[1] for r in res}

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

    async def get_user_configs(self) -> List[UserConfig]:
        async with self._async_session() as session:
            stmt = select(models.UserConfig)
            res = await session.execute(stmt)
            res = res.unique().scalars().all()
            # print(res[0].to_dict())
            res = [UserConfig(**r.to_dict()) for r in res]
            return res

    # Delete functions

    async def del_custom_datas(self, key: str, ids: List[str] = None):
        async with self._async_session() as session:
            stmt = delete(models.CustomData).filter(models.CustomData.key == key)
            if ids:
                stmt = stmt.filter(models.CustomData.id.in_(ids))
            await session.execute(stmt)
            await session.commit()

    async def del_user_configs(self, names: List[str]):
        async with self._async_session() as session:
            stmt = delete(models.UserConfig).filter(models.UserConfig.name.in_(names))
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
    async def _update_rules(session: any, rules: List[Rule]) -> Tuple[Set[int], Set[int]]:
        """
        Updates collected tweets info for the given Rules
        """
        added = set()
        updated = set()
        for rule in rules:

            collected_in_db = await PostgresStorage._get_collected_from_rule(session, rule.collected_tweets_list())
            collected_dict = {t.rule_tweet_id(): t for t in collected_in_db}

            for collected in rule.collected_tweets_list():
                if collected.rule_tweet_id() in collected_dict:
                    pg_collected = collected_dict[collected.rule_tweet_id()]
                    if collected.direct_hit and not pg_collected.direct_hit:
                        pg_collected.direct_hit = True
                else:
                    pg_collected = models.CollectedTweet()
                    pg_collected.rule_id = rule.id
                    pg_collected.tweet_id = collected.tweet_id
                    pg_collected.collected_at = collected.collected_at
                    # Override only if True
                    if collected.direct_hit:
                        pg_collected.direct_hit = collected.direct_hit

                await session.merge(pg_collected)

            updated.add(rule.id)
        return added, updated

    @staticmethod
    async def _get_rule(session, rule: Rule) -> models.Rule:
        stmt = select(models.Rule)
        stmt = stmt.filter(models.Rule.query == rule.query)
        res = await session.execute(stmt)
        res = res.scalars().first()
        return res

    @staticmethod
    async def _get_collected_from_rule(session, collected_list: List[CollectedTweet]):
        collected_tuple = [(t.rule_id, t.tweet_id) for t in collected_list]
        stmt = select(models.CollectedTweet)
        stmt = stmt.filter(tuple_(models.CollectedTweet.rule_id, models.CollectedTweet.tweet_id).in_(collected_tuple))
        res = await session.execute(stmt)
        res = res.scalars().all()
        return res

    # TODO: allow modification of rule TAGS
    async def request_rules(self, rules: List[Rule]):
        async with self._async_session() as session:
            for rule in rules:
                pg_rule = await self._get_rule(session, rule)
                if not pg_rule:
                    pg_rule = models.Rule()
                    pg_rule.update(rule.dict())
                    pg_rule.created_at = datetime.datetime.now()
                    pg_rule = await session.merge(pg_rule)
                elif pg_rule.tag != rule.tag:
                    pg_rule.tag = rule.tag
                    await session.merge(pg_rule)
                await session.commit()
                rule.id = pg_rule.id
                rule.tag = pg_rule.tag
                rule.created_at = pg_rule.created_at
        return rules

    @staticmethod
    def should_save():
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
