from restweetution.models.config.query_fields import QueryFields

BASIC_CONFIG: QueryFields = QueryFields(**{
    "tweet_fields": ["attachments", "author_id", "conversation_id", "created_at", "public_metrics"]
})

MEDIUM_CONFIG: QueryFields = QueryFields(**{
    "expansions": ["author_id", "referenced_tweets.id", "in_reply_to_user_id",
                   "attachments.media_keys", "entities.mentions.username", "referenced_tweets.id.author_id"],
    "tweet_fields": ["attachments", "author_id", "conversation_id",
                     "created_at", "entities", "in_reply_to_user_id", "lang", "possibly_sensitive",
                     "public_metrics", "referenced_tweets", "reply_settings"],
    "user_fields": ["created_at", "description", "entities", "location", "pinned_tweet_id", "profile_image_url",
                    "protected", "public_metrics", "url", "verified"],
    "media_fields": ["preview_image_url", "public_metrics", "alt_text", "url"]
})

ALL_CONFIG: QueryFields = QueryFields(**{
    "expansions": ["author_id", "referenced_tweets.id", "in_reply_to_user_id",
                   "attachments.media_keys", "attachments.poll_ids", "geo.place_id",
                   "entities.mentions.username", "referenced_tweets.id.author_id"],
    "tweet_fields": ["attachments", "author_id", "context_annotations", "conversation_id",
                     "created_at", "entities", "geo", "in_reply_to_user_id", "lang", "possibly_sensitive",
                     "public_metrics", "referenced_tweets", "reply_settings", "source", "withheld"],
    "user_fields": ["created_at", "description", "entities", "location", "pinned_tweet_id", "profile_image_url",
                    "protected", "public_metrics", "url", "verified", "withheld"],
    "media_fields": ["duration_ms", "height", "preview_image_url", "public_metrics", "width", "alt_text", "url"],
    "place_fields": ["contained_within", "country", "country_code", "geo", "name", "place_type"],
    "poll_fields": ["duration_minutes", "end_datetime", "voting_status"]
})
