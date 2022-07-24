from datetime import datetime
from typing import List

from pydantic import BaseModel


class PollOption(BaseModel):
    position: int
    label: str
    votes: int


class Poll(BaseModel):
    id: str
    options: List[PollOption]
    duration_minutes: int
    end_datetime: datetime
    voting_status: str
