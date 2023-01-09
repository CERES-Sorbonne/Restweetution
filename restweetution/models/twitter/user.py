from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List, Any

from restweetution.models.twitter.entities import Tag, Url


@dataclass
class UserHashtags:
    hashtags: Optional[List[Tag]] = None


@dataclass
class UserMetrics:
    followers_count: int
    following_count: int
    tweet_count: int
    listed_count: int


@dataclass
class UserUrls:
    urls: List[Url] = None


@dataclass
class UserEntity:
    url: Optional[UserUrls] = None
    description: Optional[UserHashtags] = None


@dataclass
class User:
    id: str
    name: str = None
    username: str = None
    created_at: Optional[datetime] = None
    description: Optional[str] = None
    entities: Optional[UserEntity] = None
    location: Optional[str] = None
    pinned_tweet_id: Optional[str] = None
    profile_image_url: Optional[str] = None
    protected: Optional[bool] = None
    public_metrics: Optional[UserMetrics] = None
    url: Optional[str] = None
    verified: Optional[bool] = None
    withheld: Any = None
