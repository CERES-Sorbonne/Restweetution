from datetime import datetime
from typing import List

from pydantic import BaseModel

from restweetution.models.twitter import Media, User, Place, Poll
from restweetution.models.twitter.entities import Annotation, Tag, Mention, Url, Attachments
from restweetution.models.twitter.utils import nested_dataclass


@nested_dataclass
class Entities:
    annotations: List[Annotation] = None
    cashtags: List[Tag] = None
    hashtags: List[Tag] = None
    mentions: List[Mention] = None
    urls: List[Url] = None


@nested_dataclass
class PublicMetrics:
    retweet_count: int = None
    reply_count: int = None
    like_count: int = None
    quote_count: int = None


@nested_dataclass
class Domain:
    id: str = None
    name: str = None
    description: str = None


@nested_dataclass
class ContextEntity:
    id: str = None
    name: str = None


@nested_dataclass
class ContextAnnotation:
    domain: Domain = None
    entity: ContextEntity = None


@nested_dataclass
class Coordinates:
    type: str = None
    coordinates: List[float] = None


@nested_dataclass
class Geo:
    coordinates: Coordinates = None
    place_id: str = None


@nested_dataclass
class NonPublicMetrics:
    impression_count: int = None
    url_link_clicks: int = None
    user_profile_clicks: int = None


@nested_dataclass
class OrganicMetrics:
    impression_count: int = None
    like_count: int = None
    reply_count: int = None
    retweet_count: int = None
    url_link_clicks: int = None
    user_profile_clicks: int = None


@nested_dataclass
class PromotedMetrics:
    impression_count: int = None
    like_count: int = None
    reply_count: int = None
    retweet_count: int = None
    url_link_clicks: int = None
    user_profile_clicks: int = None


@nested_dataclass
class ReferencedTweet:
    type: str = None
    id: str = None


@nested_dataclass
class Withheld:
    copyright: bool = None
    country_codes: List[str] = None
    scope: str = None


@nested_dataclass
class Tweet:
    id: str
    text: str = None
    attachments: Attachments = None
    author_id: str = None
    context_annotations: List[ContextAnnotation] = None
    conversation_id: str = None
    created_at: datetime = None
    entities: Entities = None
    geo: Geo = None
    in_reply_to_user_id: str = None
    lang: str = None
    non_public_metrics: NonPublicMetrics = None
    organic_metrics: OrganicMetrics = None
    possibly_sensitive: bool = None
    promoted_metrics: PromotedMetrics = None
    public_metrics: PublicMetrics = None
    referenced_tweets: List[ReferencedTweet] = None
    reply_settings: str = None
    source: str = None
    withheld: Withheld = None

    def retweet_id(self):
        if not self.referenced_tweets:
            return False
        retweet_id = next((ref.id for ref in self.referenced_tweets if ref.type == 'retweeted'), None)
        if not retweet_id:
            return False
        return retweet_id


@nested_dataclass
class Includes:
    media: List[Media] = None
    users: List[User] = None
    places: List[Place] = None
    polls: List[Poll] = None
    tweets: List[Tweet] = None


@nested_dataclass
class RuleId(BaseModel):
    id: str
    tag: str


@nested_dataclass
class TweetResponse(BaseModel):
    data: Tweet
    includes: Includes = None
    matching_rules: List[RuleId] = None
    errors: List[dict] = None
