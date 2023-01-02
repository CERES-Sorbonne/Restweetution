from typing import Optional

from pydantic import BaseModel

from restweetution.storages.elastic_storage.elastic_storage import ElasticStorage
from restweetution.storages.postgres_jsonb_storage.postgres_jsonb_storage import PostgresJSONBStorage


class ElasticConfig(BaseModel):
    url: str
    user: str
    pwd: str


class SystemConfig(BaseModel):
    postgres_url: str
    media_dir_path: Optional[str]
    elastic: Optional[ElasticConfig]

    def build_storage(self):
        return PostgresJSONBStorage(url=self.postgres_url)

    def build_elastic(self):
        return ElasticStorage('', self.elastic.url, self.elastic.user, self.elastic.pwd)
