import datetime

from sqlalchemy import Column, Table, TIMESTAMP, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB

from restweetution.storages.postgres_jsonb_storage.models import meta_data

TWEET_UPDATE = Table(
    "tweet_update",
    meta_data,
    Column("tweet_id", ForeignKey("tweet.id"), primary_key=True),
    Column("collected_at", TIMESTAMP(timezone=True), default=datetime.datetime.now),
    Column("data", JSONB)
)
