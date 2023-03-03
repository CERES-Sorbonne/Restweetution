from sqlalchemy import Column, Table, String
from sqlalchemy.dialects.postgresql import JSONB

from restweetution.storages.postgres_jsonb_storage.models import meta_data

PLACE = Table(
    "place",
    meta_data,
    Column("id", String, primary_key=True),
    Column("name", String),
    Column("full_name", String),

    Column("contained_within", JSONB),
    Column("country", String),
    Column("country_code", String),
    Column("geo", JSONB),
    Column("place_type", String),
)
