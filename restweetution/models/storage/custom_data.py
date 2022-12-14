from typing import Dict, List, Union

from pydantic import BaseModel


class CustomData(BaseModel):
    key: str
    id: str = None
    data: Union[Dict, List] = {}

    def unique_id(self):
        return self.key + '-' + self.id
