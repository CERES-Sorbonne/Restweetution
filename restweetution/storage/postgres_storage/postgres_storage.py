from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from restweetution.models.bulk_data import BulkData
from restweetution.storage.async_storage import AsyncStorage

from restweetution.storage.postgres_storage.models import User, Place
from restweetution.storage.postgres_storage.models.media import Media
from restweetution.storage.postgres_storage.models.poll import Poll
from restweetution.storage.postgres_storage.models.tweet import Tweet


class PostgresStorage(AsyncStorage):
    def __init__(self,
                 name: str,
                 url: str):
        """
        Storage for postgres
        :param name: Name of the storage. Human friendly identifier
        :param url: Connection string
        """
        super().__init__(name=name)

        self._engine = create_async_engine(
            url,
            echo=False,
        )
        self._async_session = sessionmaker(
            self._engine, expire_on_commit=False, class_=AsyncSession
        )

    async def bulk_save(self, data: BulkData):
        tweets = data.tweets
        async with self._async_session() as session:
            for tweet in tweets:
                pg_tweet = Tweet()
                pg_tweet.update(tweet.dict())
                await session.merge(pg_tweet)
            for user in data.users:
                pg_user = User()
                pg_user.update(user.dict())
                await session.merge(pg_user)
            for place in data.places:
                pg_place = Place()
                pg_place.update(place.dict())
                await session.merge(pg_place)
            for media in data.media:
                pg_media = Media()
                pg_media.update(media.dict())
                await session.merge(pg_media)
            for poll in data.polls:
                pg_poll = Poll()
                pg_poll.update(poll.dict())
                await session.merge(pg_poll)
            await session.commit()
