from typing import Optional

from pydantic import BaseModel


class Attachments(BaseModel):
    media_keys: Optional[list[str]]


class Entity(BaseModel):
    start: int
    end: int


class Annotation(Entity):
    probability: float
    type: str
    normalized_text: str


class Hashtag(Entity):
    tag: str


class Image(BaseModel):
    url: Optional[str]
    width: Optional[int]
    height: Optional[int]


class Url(Entity):
    url: str
    expanded_url: str
    display_url: str


class UrlEntity(Url):
    url: Optional[str]
    expanded_url: Optional[str]
    display_url: Optional[str]
    images: Optional[list[Image]]
    status: Optional[int]
    title: Optional[str]
    description: Optional[str]
    unwound_url: Optional[str]


class Entities(BaseModel):
    annotations: list[Annotation]
    hashtags: list[Hashtag]
    urls: list[UrlEntity]


class Metrics(BaseModel):
    retweet_count: int
    reply_count: int
    like_count: int
    quote_count: int


class Domain(BaseModel):
    id: str
    name: str
    description: str


class ContextEntity(BaseModel):
    id: str
    name: str


class ContextAnnotation(BaseModel):
    domain: Domain
    entity: ContextEntity


class MediaMetrics(BaseModel):
    view_count: int


class TweetData(BaseModel):
    id: str
    text: str
    lang: Optional[str]
    conversation_id: Optional[str]
    attachments: Optional[Attachments]
    possibly_sensitive: Optional[bool]
    entities: Optional[Entities]
    public_metrics: Optional[Metrics]
    context_annotations: Optional[list[ContextAnnotation]]
    source: Optional[str]
    created_at: Optional[str]


class Media(BaseModel):
    height: Optional[int]
    width: Optional[int]
    duration_ms: Optional[int]
    media_key: str
    type: str
    preview_image_url: Optional[str]
    public_metrics: Optional[MediaMetrics]


class UserUrls(BaseModel):
    urls: list[Url]


class UserHashtags(BaseModel):
    hashtags: list[Hashtag]


class UserEntity(BaseModel):
    url: UserUrls
    description: UserHashtags


class UserMetrics(BaseModel):
    followers_count: int
    following_count: int
    tweet_count: int
    listed_count: int


class User(BaseModel):
    id: str
    created_at: Optional[str]
    protected: Optional[bool]
    username: Optional[str]
    verified: Optional[bool]
    entities: Optional[list[UserEntity]]
    description: Optional[str]
    pinned_tweet_id: Optional[str]
    public_metrics: Optional[UserMetrics]
    location: Optional[str]
    name: Optional[str]
    profile_image_url: Optional[str]
    url: Optional[str]


class TweetIncludes(BaseModel):
    media: list[Media]
    users: list[User]


class Rule(BaseModel):
    id: str
    tag: str


class Tweet(BaseModel):
    data: TweetData
    includes: Optional[TweetIncludes]
    matching_rules: Optional[list[Rule]]