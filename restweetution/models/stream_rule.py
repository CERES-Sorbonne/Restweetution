from typing import List, Optional
from pydantic import BaseModel


class RuleRef(BaseModel):
    id: str
    tag: str


class StreamRule(RuleRef):
    value: Optional[str]


class RuleResponseMeta(BaseModel):
    sent: str
    result_count: int


class RuleResponse(BaseModel):
    data: List[StreamRule]
    meta: RuleResponseMeta
