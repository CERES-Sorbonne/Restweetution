import datetime

from sqlalchemy import Column, Table, String, TIMESTAMP, Boolean, ForeignKey, Integer

from restweetution.storages.postgres_jsonb_storage.models import meta_data

RULE = Table(
    "rule",
    meta_data,
    Column("id", Integer, primary_key=True),
    Column("tag", String),
    Column("query", String, unique=True, nullable=False),
    Column("created_at", TIMESTAMP(timezone=True), default=datetime.datetime.now, nullable=False),
    Column("count_estimate", Integer, default=0)
)

RULE_MATCH = Table(
    "collected_tweet",
    meta_data,
    Column("rule_id", ForeignKey("rule.id"), primary_key=True),
    Column("tweet_id", ForeignKey("tweet.id"), primary_key=True),
    Column("tweet_created_at", nullable=False),

    Column("collected_at", TIMESTAMP(timezone=True), nullable=False),
    Column("direct_hit", Boolean)
)
