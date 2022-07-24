from typing import List, Optional

from pydantic import BaseModel


class Place(BaseModel):
    full_name: str
    id: str
    contained_within: Optional[List[str]]
    country: Optional[str]
    country_code: Optional[str]
    geo: Optional[dict]
    name: Optional[str]
    place_type: Optional[str]
