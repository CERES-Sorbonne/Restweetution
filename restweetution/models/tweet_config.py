from typing import Literal, Optional

from pydantic import BaseModel

Expansion = Literal["author_id", "referenced_tweets.id", "in_reply_to_user_id",
                    "attachments.media_keys", "attachments.poll_ids", "geo.place_id",
                    "entities.mentions.username", "referenced_tweets.id.author_id"]

TweetField = Literal["attachments", "author_id", "context_annotations", "conversation_id",
                     "created_at", "entities", "geo", "in_reply_to_user_id", "lang", "possibly_sensitive",
                     "public_metrics", "referenced_tweets", "reply_settings", "source", "withheld"]

UserField = Literal["created_at", "description", "entities", "location", "pinned_tweet_id", "profile_image_url",
                    "protected", "public_metrics", "url", "verified", "withheld"]

MediaField = Literal["duration_ms", "height", "preview_image_url", "public_metrics", "width", "alt_text", "url"]


class TweetConfig(BaseModel):
    expansions: Optional[list[Expansion]]
    tweetFields: Optional[list[TweetField]]
    mediaFields: Optional[list[MediaField]]
    userFields: Optional[list[UserField]]
