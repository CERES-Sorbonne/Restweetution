from sqlalchemy import Column, Table, String, Boolean, TIMESTAMP, Integer
from sqlalchemy.dialects.postgresql import JSONB

from restweetution.storages.postgres_jsonb_storage.models import meta_data

MEDIA = Table(
    "media",
    meta_data,
    Column("media_key", String, primary_key=True),
    Column("type", String),
    Column("url", String),
    Column("preview_image_url", String),
    Column("duration_ms", Integer),
    Column("height", Integer),
    Column("width", Integer),
    Column("alt_text", String),
    Column("variants", JSONB),
    Column("non_public_metrics", JSONB),
    Column("organic_metrics", JSONB),
    Column("promoted_metrics", JSONB),
    Column("public_metrics", JSONB),
    Column("promoted_metrics", JSONB),
)