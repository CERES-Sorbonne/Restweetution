from sqlalchemy import Column, Table, String, Integer, TIMESTAMP
from sqlalchemy.dialects.postgresql import JSONB

from restweetution.storages.postgres_jsonb_storage.models import meta_data

POLL = Table(
    "poll",
    meta_data,
    Column("id", String, primary_key=True),
    Column("duration_minutes", Integer),
    Column("end_datetime", TIMESTAMP(timezone=True)),
    Column("voting_status", String),
    Column("options", JSONB),
)