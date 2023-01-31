from typing import Optional, Dict

from pydantic import BaseModel


class InstanceUpdate(BaseModel):
    source: str
    user_id: str = ''
    data: Optional[Dict]
