from typing import Optional, List

from pydantic import BaseModel


class Entity(BaseModel):
    start: int
    end: int


class Image(BaseModel):
    url: Optional[str]
    width: Optional[int]
    height: Optional[int]


class Url(Entity):
    url: Optional[str]
    expanded_url: str
    display_url: str
    status: Optional[str]
    title: Optional[str]
    description: Optional[str]
    unwound_url: Optional[str]
    images: Optional[List[Image]]


class Annotation(Entity):
    probability: float
    type: str
    normalized_text: str


class Tag(Entity):
    """Class for Hashtag, Cashtag"""
    tag: str


class Mention(Entity):
    username: str
