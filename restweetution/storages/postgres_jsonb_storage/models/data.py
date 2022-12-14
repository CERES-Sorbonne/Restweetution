from sqlalchemy import Column, Table, String
from sqlalchemy.dialects.postgresql import JSONB

from restweetution.storages.postgres_jsonb_storage.models import meta_data

DATA = Table(
    "data",
    meta_data,
    Column("key", String, primary_key=True),
    Column("id", String, primary_key=True),
    Column("data", JSONB),
)