from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel

from restweetution.models.twitter.entities import Annotation, Tag, Url, Mention
from restweetution.models.twitter.media import Media
from restweetution.models.rule import StreamAPIRule
from restweetution.models.twitter.place import Place
from restweetution.models.twitter.poll import Poll
from restweetution.models.twitter.user import User


class Attachments(BaseModel):
    media_keys: List[str] = []
    poll_ids: List[str] = []


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
    scope: str


class Tweet(BaseModel):
    id: str
    text: Optional[str]
    attachments: Optional[Attachments] = Attachments()
    author_id: Optional[str]
    context_annotations: Optional[List[ContextAnnotation]]
    conversation_id: Optional[str]
    created_at: Optional[datetime]
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


class Includes(BaseModel):
    media: List[Media] = []
    users: List[User] = []
    places: List[Place] = []
    polls: List[Poll] = []
    tweets: List[Tweet] = []


class TweetResponse(BaseModel):
    data: Tweet
    includes: Optional[Includes]
    matching_rules: Optional[List[StreamAPIRule]]
    errors: Optional[List[dict]]
