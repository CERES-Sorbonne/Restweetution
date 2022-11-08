tweet_fields = [
    'id',
    'text',
    'created_at',
    'author_id',
    'conversation_id',
    'in_reply_to_user_id',
    'referenced_tweets',
    'attachments',
    'geo',
    'context_annotations',
    'entities',
    'withheld',
    'public_metrics',
    'organic_metrics',
    'promoted_metrics',
    'possibly_sensitive',
    'lang',
    'source',
    'reply_settings'
]

user_fields = [
    'id',
    'name',
    'username',
    'created_at',
    'description',
    'entities_url_urls',
    'entities_description',
    'location',
    'pinned_tweet_id',
    'profile_image_url',
    'protected',
    'public_metrics',
    'url',
    'verified',
    'withheld'
]

media_fields = [
    'media_key',
    'type',
    'url',
    'duration_ms',
    'height',
    'non_public_metrics',
    'organic_metrics',
    'preview_image_url',
    'promoted_metrics',
    'public_metrics',
    'width',
    'alt_text',
    'variants',
    'sha1',
    'format'
]
place_fields = [
    "id",
    "full_name",
    "contained_within",
    "country",
    "country_code",
    "geo",
    "name",
    "place_type"
]
poll_fields = [
    "id",
    "options",
    "duration_minutes",
    "end_datetime",
    "voting_status"
]

rule_fields = [
    'id',
    'type',
    'tag',
    'query',
    'created_at',
    'collected_tweets',
]
