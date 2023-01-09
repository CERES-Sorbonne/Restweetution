from dataclasses import dataclass
from typing import List, Optional


@dataclass
class Place:
    full_name: str
    id: str
    contained_within: Optional[List[str]] = None
    country: Optional[str] = None
    country_code: Optional[str] = None
    geo: Optional[dict] = None
    name: Optional[str] = None
    place_type: Optional[str] = None
