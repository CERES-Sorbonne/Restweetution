from typing import Optional

from pydantic import BaseModel


class ElasticConfig(BaseModel):
    url: str
    user: str
    pwd: str


class SystemConfig(BaseModel):
    postgres_url: str
    media_dir_path: Optional[str]
    elastic: Optional[ElasticConfig]

