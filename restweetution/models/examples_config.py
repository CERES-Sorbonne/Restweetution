from restweetution.models.tweet_config import TweetConfig

BASIC_CONFIG: TweetConfig = TweetConfig(**{
    "tweetFields": ["attachments", "author_id", "conversation_id", "created_at", "public_metrics"]
})

MEDIUM_CONFIG: TweetConfig = TweetConfig(**{
    "expansions": ["author_id", "referenced_tweets.id", "in_reply_to_user_id",
                   "attachments.media_keys", "entities.mentions.username", "referenced_tweets.id.author_id"],
    "tweetFields": ["attachments", "author_id", "conversation_id",
                    "created_at", "entities", "in_reply_to_user_id", "lang", "possibly_sensitive",
                    "public_metrics", "referenced_tweets", "reply_settings"],
    "userFields": ["created_at", "description", "entities", "location", "pinned_tweet_id", "profile_image_url",
                   "protected", "public_metrics", "url", "verified"],
    "mediaFields": ["preview_image_url", "public_metrics", "alt_text", "url"]
})

ALL_CONFIG: TweetConfig = TweetConfig(**{
    "expansions": ["author_id", "referenced_tweets.id", "in_reply_to_user_id",
                   "attachments.media_keys", "attachments.poll_ids", "geo.place_id",
                   "entities.mentions.username", "referenced_tweets.id.author_id"],
    "tweetFields": ["attachments", "author_id", "context_annotations", "conversation_id",
                    "created_at", "entities", "geo", "in_reply_to_user_id", "lang", "possibly_sensitive",
                    "public_metrics", "referenced_tweets", "reply_settings", "source", "withheld"],
    "userFields": ["created_at", "description", "entities", "location", "pinned_tweet_id", "profile_image_url",
                   "protected", "public_metrics", "url", "verified", "withheld"],
    "mediaFields": ["duration_ms", "height", "preview_image_url", "public_metrics", "width", "alt_text", "url"]
})
