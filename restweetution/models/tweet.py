from typing import Optional, List

from pydantic import BaseModel

from .entities import Annotation, Tag, Url, Mention
from .media import Media
from .user import User


class Attachments(BaseModel):
    media_keys: Optional[List[str]]
    poll_ids: Optional[List[str]]


class Entities(BaseModel):
    annotations: Optional[List[Annotation]]
    cashtags: Optional[List[Tag]]
    hashtags: Optional[List[Tag]]
    mentions: Optional[List[Mention]]
    urls: Optional[List[Url]]


class PublicMetrics(BaseModel):
    retweet_count: int
    reply_count: int
    like_count: int
    quote_count: int


class Domain(BaseModel):
    id: str
    name: str
    description: Optional[str]


class ContextEntity(BaseModel):
    id: str
    name: str


class ContextAnnotation(BaseModel):
    domain: Domain
    entity: ContextEntity


class Coordinates(BaseModel):
    type: str
    coordinates: List[float]


class Geo(BaseModel):
    coordinates: Optional[Coordinates]
    place_id: Optional[str]


class NonPublicMetrics(BaseModel):
    impression_count: int
    url_link_clicks: int
    user_profile_clicks: int


class OrganicMetrics(BaseModel):
    impression_count: int
    like_count: int
    reply_count: int
    retweet_count: int
    url_link_clicks: int
    user_profile_clicks: int


class PromotedMetrics(BaseModel):
    impression_count: int
    like_count: int
    reply_count: int
    retweet_count: int
    url_link_clicks: int
    user_profile_clicks: int


class ReferencedTweet(BaseModel):
    type: str
    id: str


class Withheld(BaseModel):
    copyright: bool
    country_codes: List[str]


class Tweet(BaseModel):
    id: str
    text: str
    attachments: Optional[Attachments]
    author_id: str
    context_annotations: Optional[List[ContextAnnotation]]
    conversation_id: Optional[str]
    created_at: Optional[str]
    entities: Optional[Entities]
    geo: Optional[Geo]
    in_reply_to_user_id: Optional[str]
    lang: Optional[str]
    non_public_metrics: Optional[NonPublicMetrics]
    organic_metrics: Optional[OrganicMetrics]
    possibly_sensitive: Optional[bool]
    promoted_metrics: Optional[PromotedMetrics]
    public_metrics: Optional[PublicMetrics]
    referenced_tweets: Optional[List[ReferencedTweet]]
    reply_settings: Optional[str]
    source: Optional[str]
    withheld: Optional[Withheld]


class TweetIncludes(BaseModel):
    media: Optional[List[Media]]
    users: Optional[List[User]]


class Rule(BaseModel):
    id: str
    tag: str


class TweetResponse(BaseModel):
    tweet: Tweet
    includes: Optional[TweetIncludes]
    matching_rules: Optional[List[Rule]]
    errors: Optional[List[dict]]


class SavedTweet(Tweet):
    matching_rules: Optional[List[Rule]]


class StreamRule(Rule):
    value: str
