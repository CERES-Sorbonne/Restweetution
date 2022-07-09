from datetime import datetime
from typing import Optional, List, Any

from pydantic import BaseModel

from restweetution.models.twitter.entities import Tag, Url


class UserHashtags(BaseModel):
    hashtags: Optional[List[Tag]]


class UserMetrics(BaseModel):
    followers_count: int
    following_count: int
    tweet_count: int
    listed_count: int


class UserUrls(BaseModel):
    urls: List[Url]


class UserEntity(BaseModel):
    url: Optional[UserUrls]
    description: Optional[UserHashtags]


class User(BaseModel):
    id: str
    name: str
    username: str
    created_at: Optional[datetime]
    description: Optional[str]
    entities: Optional[UserEntity]
    location: Optional[str]
    pinned_tweet_id: Optional[str]
    profile_image_url: Optional[str]
    protected: Optional[bool]
    public_metrics: Optional[UserMetrics]
    url: Optional[str]
    verified: Optional[bool]
    withheld: Any
