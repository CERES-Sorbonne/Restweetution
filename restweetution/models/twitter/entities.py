from dataclasses import dataclass, field
from typing import Optional, List

from restweetution.models.twitter import nested_dataclass


@dataclass
class Entity:
    start: int
    end: int


@dataclass
class Annotation(Entity):
    probability: float
    type: str
    normalized_text: str


@dataclass
class Tag(Entity):
    """Class for Hashtag, Cashtag"""
    tag: str


@dataclass
class Mention(Entity):
    username: str


@nested_dataclass
class Attachments:
    media_keys: List[str] = field(default_factory=list)
    poll_ids: List[str] = field(default_factory=list)


@dataclass
class Image:
    url: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None


@dataclass
class Url(Entity):
    url: Optional[str] = None
    expanded_url: Optional[str] = None
    display_url: Optional[str] = None
    status: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    unwound_url: Optional[str] = None
    images: Optional[List[Image]] = None

