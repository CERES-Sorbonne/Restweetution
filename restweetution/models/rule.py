from typing import List
from pydantic import BaseModel


class Rule(BaseModel):
    id: str
    tag: str
    value: str


class RuleResponseMeta(BaseModel):
    sent: str
    result_count: int


class RuleResponse(BaseModel):
    data: List[Rule]
    meta: RuleResponseMeta
