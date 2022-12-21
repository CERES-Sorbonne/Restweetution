from sqlalchemy import Column, Table, String, ForeignKey

from restweetution.storages.postgres_jsonb_storage.models import meta_data

DOWNLOADED_MEDIA = Table(
    "downloaded_media",
    meta_data,
    Column("media_key", String, ForeignKey("media.media_key"), primary_key=True),
    Column("sha1", String),
    Column("format", String)
)