from pathlib import Path
from typing import Optional

from pydantic import BaseModel

from restweetution.storages.elastic_storage.elastic_storage import ElasticStorage
from restweetution.storages.exporter.csv_exporter import CSVExporter
from restweetution.storages.postgres_jsonb_storage.postgres_jsonb_storage import PostgresJSONBStorage


class ElasticConfig(BaseModel):
    url: str
    user: str
    pwd: str


class SystemConfig(BaseModel):
    postgres_url: str
    media_dir_path: Optional[str]
    elastic: Optional[ElasticConfig]
    resource_root_dir: Optional[str]
    public_base_path: Optional[str]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.public_base_path:
            self.public_base_path = self.resource_root_dir

    def build_storage(self):
        return PostgresJSONBStorage(url=self.postgres_url)

    def build_elastic_exporter(self):
        return ElasticStorage('', self.elastic.url, self.elastic.user, self.elastic.pwd)

    def build_csv_exporter(self, sub_folder: str = None):
        if not sub_folder:
            sub_folder = ''
        path = self.get_resource_path() / 'export_csv' / sub_folder

        return CSVExporter(root_dir=path)

    def get_resource_path(self):
        if not self.resource_root_dir:
            raise ValueError('resource_root_dir must be set inside SystemConfig')
        return Path(self.resource_root_dir)

    def convert_local_to_public_url(self, path: str):
        return path.replace(self.resource_root_dir, self.public_base_path)

