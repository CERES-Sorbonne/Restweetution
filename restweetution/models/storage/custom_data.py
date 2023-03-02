from typing import Dict, Union

from pydantic import BaseModel


class CustomData(BaseModel):
    key: str
    id: str = None
    data: Union[Dict] = {}

    def unique_id(self):
        return self.key + '-' + self.id
