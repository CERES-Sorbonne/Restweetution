from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class PollOption(BaseModel):
    position: int
    label: str
    votes: int


class Poll(BaseModel):
    id: str
    options: List[PollOption]
    duration_minutes: Optional[int]
    end_datetime: Optional[datetime]
    voting_status: Optional[str]
