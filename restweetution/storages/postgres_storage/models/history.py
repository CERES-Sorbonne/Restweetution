from sqlalchemy import Column, String, Integer
from sqlalchemy.dialects.postgresql import TIMESTAMP

from restweetution.storages.postgres_storage.models import Base


class TweetPublicMetricsHistory(Base):
    __tablename__ = 'tweet_public_metrics_history'

    parent_id = Column(String, primary_key=True)
    timestamp = Column(TIMESTAMP(timezone=True), primary_key=True)

    retweet_count = Column(Integer)
    reply_count = Column(Integer)
    like_count = Column(Integer)
    quote_count = Column(Integer)
