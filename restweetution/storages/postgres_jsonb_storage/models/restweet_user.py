from sqlalchemy import Column, Table, String
from sqlalchemy.dialects.postgresql import JSONB

from restweetution.storages.postgres_jsonb_storage.models import meta_data

RESTWEET_USER = Table(
    "restweet_user",
    meta_data,
    Column("name", String, primary_key=True),
    Column("bearer_token", String, unique=True),
    Column("searcher_state", JSONB),
    Column("streamer_state", JSONB)
)