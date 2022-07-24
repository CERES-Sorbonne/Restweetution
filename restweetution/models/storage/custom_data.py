from typing import Dict

from pydantic import BaseModel


class CustomData(BaseModel):
    key: str
    id: str = "0"
    data: Dict = {}

    def unique_id(self):
        return self.key + '-' + self.id
