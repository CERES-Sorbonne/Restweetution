import datetime

from sqlalchemy import Column, Table, String, Integer, TIMESTAMP
from sqlalchemy.dialects.postgresql import JSONB

from restweetution.storages.postgres_jsonb_storage.models import meta_data

ERROR = Table(
    "error",
    meta_data,
    Column("id", Integer, primary_key=True),
    Column("error_name", String),
    Column("traceback", String),
    Column("data", JSONB),
    Column("created_at", TIMESTAMP(timezone=True), default=datetime.datetime.now)
)