from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from restweetution.errors import handle_storage_save_error
from restweetution.models.bulk_data import BulkData
from restweetution.storage.document_storage import DocumentStorage
from restweetution.storage.postgres_storage.models import User, Place, Rule, Error
from restweetution.storage.postgres_storage.models.media import Media
from restweetution.storage.postgres_storage.models.poll import Poll
from restweetution.storage.postgres_storage.models.rule import CollectedTweet
from restweetution.storage.postgres_storage.models.tweet import Tweet


class PostgresStorage(DocumentStorage):
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

    async def save_error(self, error: any):
        async with self._async_session() as session:
            pg_error = Error()
            pg_error.data = error
            session.add(pg_error)
            await session.commit()

    @handle_storage_save_error()
    async def bulk_save(self, data: BulkData):
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
            for key in data.media:
                pg_media = Media()
                pg_media.update(data.media[key].dict())
                await session.merge(pg_media)
            for key in data.polls:
                pg_poll = Poll()
                pg_poll.update(data.polls[key].dict())
                await session.merge(pg_poll)
            for key in data.rules:
                await self._add_or_update_rule(session, data.rules[key])

            await session.commit()
            print(f'Postgres saved: {len(data.tweets.items())} tweets, {len(data.users.items())} users')

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
                session.add(pg_collected)
