from typing import List, Optional

from pydantic import BaseModel


class StorageConfig(BaseModel):
    type: str
    name: str
    tags: List[str] = []


class ElasticConfig(StorageConfig):
    type = 'elastic'
    url: str
    es_user: Optional[str]
    es_pwd: Optional[str]
