from typing import Dict

from pydantic import BaseModel


class SystemConfig(BaseModel):
    storage: Dict
    media_dir_path: str


