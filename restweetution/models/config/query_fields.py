from typing import Literal, Optional, List

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

PlaceField = Literal["contained_within", "country", "country_code", "geo", "name", "place_type"]

PollField = Literal["duration_minutes", "end_datetime", "voting_status"]


class QueryFields(BaseModel):
    expansions: Optional[List[Expansion]]
    tweet_fields: Optional[List[TweetField]]
    media_fields: Optional[List[MediaField]]
    user_fields: Optional[List[UserField]]
    place_fields: Optional[List[PlaceField]]
    poll_fields: Optional[List[PollField]]

    def twitter_format(self, join='_', **kwargs):
        res = {}
        if self.expansions:
            res['expansions'] = ",".join(self.expansions)
        if self.tweet_fields:
            res['tweet' + join + 'fields'] = ",".join(self.tweet_fields)
        if self.user_fields:
            res['user' + join + 'fields'] = ",".join(self.user_fields)
        if self.media_fields:
            res['media' + join + 'fields'] = ",".join(self.media_fields)
        if self.place_fields:
            res['place' + join + 'fields'] = ",".join(self.place_fields)
        if self.poll_fields:
            res['poll' + join + 'fields'] = ','.join(self.poll_fields)

        return res

