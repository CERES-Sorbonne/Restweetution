from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional


@dataclass
class PollOption:
    position: int
    label: str
    votes: int


@dataclass
class Poll:
    id: str
    options: List[PollOption]
    duration_minutes: Optional[int] = None
    end_datetime: Optional[datetime] = None
    voting_status: Optional[str] = None
