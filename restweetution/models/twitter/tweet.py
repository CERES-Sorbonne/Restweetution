from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel

from restweetution.models.twitter.entities import Annotation, Tag, Url, Mention
from restweetution.models.twitter.media import Media
from restweetution.models.twitter.place import Place
from restweetution.models.twitter.poll import Poll
from restweetution.models.twitter.user import User


class Attachments(BaseModel):
    media_keys: List[str] = []
    poll_ids: List[str] = []


class Entities(BaseModel):
    annotations: Optional[List[Annotation]] = []
    cashtags: Optional[List[Tag]] = []
    hashtags: Optional[List[Tag]] = []
    mentions: Optional[List[Mention]] = []
    urls: Optional[List[Url]] = []


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
    copyright: Optional[bool]
    country_codes: Optional[List[str]]
    scope: Optional[str]


class Tweet(BaseModel):
    id: str
    text: Optional[str]
    attachments: Optional[Attachments]
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

    def get_media_keys(self):
        if not self.attachments:
            return []
        return self.attachments.media_keys

    def get_poll_ids(self):
        if not self.attachments:
            return []
        return self.attachments.poll_ids

    def get_hashtags(self):
        if not self.entities:
            return []
        return self.entities.hashtags

    def get_cashtags(self):
        if not self.entities:
            return []
        return self.entities.cashtags

    def get_mentions(self):
        if not self.entities:
            return []
        return self.entities.mentions

    def get_annotations(self):
        if not self.entities:
            return []
        return self.entities.annotations

    def get_urls(self):
        if not self.entities:
            return []
        return self.entities.urls

    def get_quote_count(self):
        if not self.public_metrics:
            return None
        return self.public_metrics.quote_count

    def get_retweet_count(self):
        if not self.public_metrics:
            return None
        return self.public_metrics.retweet_count

    def get_reply_count(self):
        if not self.public_metrics:
            return None
        return self.public_metrics.reply_count

    def get_like_count(self):
        if not self.public_metrics:
            return None
        return self.public_metrics.like_count

    def get_retweeted_id(self):
        if not self.referenced_tweets:
            return None
        retweet_id = next((ref.id for ref in self.referenced_tweets if ref.type == 'retweeted'), None)
        if not retweet_id:
            return None
        return retweet_id

    def get_quoted_id(self):
        if not self.referenced_tweets:
            return None
        quoted_id = next((ref.id for ref in self.referenced_tweets if ref.type == 'quoted'), None)
        if not quoted_id:
            return False
        return quoted_id

    def get_replied_to_id(self):
        if not self.referenced_tweets:
            return None
        replied_to_id = next((ref.id for ref in self.referenced_tweets if ref.type == 'replied_to'), None)
        if not replied_to_id:
            return None
        return replied_to_id


class Includes(BaseModel):
    media: List[Media] = []
    users: List[User] = []
    places: List[Place] = []
    polls: List[Poll] = []
    tweets: List[Tweet] = []


class RuleId(BaseModel):
    id: str
    tag: str


class TweetResponse(BaseModel):
    data: Tweet
    includes: Optional[Includes]
    matching_rules: Optional[List[RuleId]]
    errors: Optional[List[dict]]
