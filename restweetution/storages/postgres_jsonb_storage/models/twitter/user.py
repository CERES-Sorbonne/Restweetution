from sqlalchemy import Column, Table, String, Boolean, TIMESTAMP
from sqlalchemy.dialects.postgresql import JSONB

from restweetution.storages.postgres_jsonb_storage.models import meta_data

USER = Table(
    "user",
    meta_data,
    Column("id", String, primary_key=True),
    Column("name", String),
    Column("username", String),
    Column("created_at", TIMESTAMP(timezone=True)),
    Column("description", String),
    Column("entities", JSONB),
    Column("location", String),
    Column("pinned_tweet_id", String),
    Column("profile_image_url", String),
    Column("protected", Boolean),
    Column("public_metrics", JSONB),
    Column("url", String),
    Column("verified", Boolean),
    Column("withheld", JSONB),
)
