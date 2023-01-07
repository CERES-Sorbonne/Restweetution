from sqlalchemy import Boolean
from sqlalchemy import Table, Column, String, TIMESTAMP
from sqlalchemy.dialects.postgresql import JSONB

from restweetution.storages.postgres_jsonb_storage.models.meta_data import meta_data

TWEET = Table(
    "tweet",
    meta_data,
    Column("id", String, primary_key=True),
    Column('text', String),
    Column('author_id', String),
    Column('created_at', TIMESTAMP(timezone=True), index=True),
    Column('conversation_id', String),
    Column("in_reply_to_user_id", String),
    Column("lang", String),
    Column("possibly_sensitive", Boolean),
    Column("reply_settings", String),
    Column("source", String),

    Column("attachments", JSONB),
    Column("context_annotations", JSONB),
    Column("entities", JSONB),
    Column("referenced_tweets", JSONB),

    Column("geo", JSONB),

    Column("public_metrics", JSONB),
    Column("non_public_metrics", JSONB),
    Column("organic_metrics", JSONB),
    Column("promoted_metrics", JSONB),

    Column("withheld", JSONB)
)