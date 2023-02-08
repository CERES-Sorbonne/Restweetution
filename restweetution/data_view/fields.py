class TweetFields:
    ID = 'id'
    CREATED_AT = 'created_at'
    TEXT = 'text'

    AUTHOR_ID = 'author_id'
    AUTHOR_USERNAME = 'author_username'
    CONVERSATION_ID = 'conversation_id'
    IN_REPLY_TO_USER_ID = 'in_reply_to_user_id'
    IN_REPLY_TO_USERNAME = 'in_reply_to_username'

    REFERENCED_TWEETS_TYPES = 'referenced_tweets_types'
    REFERENCED_TWEETS_IDS = 'referenced_tweets_ids'
    REFERENCED_TWEETS_AUTHOR_IDS = 'referenced_tweets_authors'
    REFERENCED_TWEETS_AUTHOR_USERNAMES = 'referenced_tweets_authors_usernames'

    LANG = 'lang'
    CONTEXT_DOMAINS = 'context_domains'
    CONTEXT_ENTITIES = 'context_entities'
    ANNOTATIONS = 'annotations'
    CASHTAGS = 'cashtags'
    HASHTAGS = 'hashtags'
    MENTIONS = 'mentions'
    URLS = 'urls'

    POLL_IDS = 'poll_ids'

    MEDIA_KEYS = 'media_keys'
    MEDIA_SHA1S = 'media_sha1s'
    MEDIA_FORMATS = 'media_formats'
    MEDIA_TYPES = 'media_types'
    MEDIA_FILES = 'media_files'

    COORDINATES = 'coordinates'
    PLACE_ID = 'place_id'

    POSSIBLY_SENSITIVE = 'possibly_sensitive'
    RETWEET_COUNT = 'retweet_count'
    REPLY_COUNT = 'reply_count'
    LIKE_COUNT = 'like_count'
    QUOTE_COUNT = 'quote_count'

    WITHHELD_COPYRIGHT = 'withheld_copyright'
    WITHHELD_COUNTRY_CODES = 'withheld_country_codes'
    WITHHELD_SCOPE = 'withheld_scope'

    REPLY_SETTINGS = 'reply_settings'
    SOURCE = 'source'

    RULE_TAGS = 'rule_tags'


class MediaFields:
    MEDIA_KEY = 'media_key'
    TYPE = 'type'

    SHA1 = 'sha1'
    FILE = 'file'
    FORMAT = 'format'

    TWEETS_ID = 'tweets_id'
    TWEETS_CREATED_AT = 'tweets_created_at'
    TWEETS_TEXT = 'tweets_text'

    TWEETS_AUTHOR_ID = 'tweets_author_id'
    TWEETS_AUTHOR_USERNAME = 'tweets_author_username'
    TWEETS_CONVERSATION_ID = 'tweets_conversation_id'
    TWEETS_IN_REPLY_TO_USER_ID = 'tweets_in_reply_to_user_id'
    TWEETS_IN_REPLY_TO_USERNAME = 'tweets_in_reply_to_username'

    TWEETS_REFERENCED_TWEETS_TYPES = 'tweets_referenced_tweets_types'
    TWEETS_REFERENCED_TWEETS_IDS = 'tweets_referenced_tweets_ids'
    TWEETS_REFERENCED_TWEETS_AUTHOR_IDS = 'tweets_referenced_tweets_authors'
    TWEETS_REFERENCED_TWEETS_AUTHOR_USERNAMES = 'tweets_referenced_tweets_authors_usernames'

    TWEETS_LANG = 'tweets_lang'
    TWEETS_CONTEXT_DOMAINS = 'tweets_context_domains'
    TWEETS_CONTEXT_ENTITIES = 'tweets_context_entities'
    TWEETS_ANNOTATIONS = 'tweets_annotations'
    TWEETS_CASHTAGS = 'tweets_cashtags'
    TWEETS_HASHTAGS = 'tweets_hashtags'
    TWEETS_MENTIONS = 'tweets_mentions'
    TWEETS_URLS = 'tweets_urls'

    TWEETS_POLL_IDS = 'tweets_poll_ids'

    TWEETS_COORDINATES = 'tweets_coordinates'
    TWEETS_PLACE_ID = 'tweets_place_id'

    TWEETS_POSSIBLY_SENSITIVE = 'possibly_sensitive'
    TWEETS_RETWEET_COUNT = 'tweets_retweet_count'
    TWEETS_REPLY_COUNT = 'tweets_reply_count'
    TWEETS_LIKE_COUNT = 'tweets_like_count'
    TWEETS_QUOTE_COUNT = 'tweets_quote_count'

    TWEETS_WITHHELD_COPYRIGHT = 'tweets_withheld_copyright'
    TWEETS_WITHHELD_COUNTRY_CODES = 'tweets_withheld_country_codes'
    TWEETS_WITHHELD_SCOPE = 'tweets_withheld_scope'

    TWEETS_REPLY_SETTINGS = 'tweets_reply_settings'
    TWEETS_SOURCE = 'tweets_source'

    TWEETS_RULE_TAGS = 'tweets_rule_tags'
