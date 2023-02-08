from typing import List

from restweetution.collection import CollectionTree, TweetNode
from restweetution.data_view.data_view2 import DataView2, ViewDict, get_safe_set, get_any_field

ID = 'id'
TEXT = 'text'
MEDIA_KEYS = 'media_keys'
MEDIA_SHA1S = 'media_sha1s'
MEDIA_FORMAT = 'media_format'
MEDIA_TYPES = 'media_types'
MEDIA_FILES = 'media_files'
POLL_IDS = 'poll_ids'
AUTHOR_ID = 'author_id'
AUTHOR_USERNAME = 'author_username'
CONTEXT_DOMAINS = 'context_domains'
CONTEXT_ENTITIES = 'context_entities'
CONVERSATION_ID = 'conversation_id'
CREATED_AT = 'created_at'
ANNOTATIONS = 'annotations'
CASHTAGS = 'cashtags'
HASHTAGS = 'hashtags'
MENTIONS = 'mentions'
URLS = 'urls'
COORDINATES = 'coordinates'
PLACE_ID = 'place_id'
IN_REPLY_TO_USER_ID = 'in_reply_to_user_id'
IN_REPLY_TO_USERNAME = 'in_reply_to_username'
LANG = 'lang'
POSSIBLY_SENSITIVE = 'possibly_sensitive'
RETWEET_COUNT = 'retweet_count'
REPLY_COUNT = 'reply_count'
LIKE_COUNT = 'like_count'
QUOTE_COUNT = 'quote_count'
REFERENCED_TWEETS_TYPES = 'referenced_tweets_types'
REFERENCED_TWEETS_IDS = 'referenced_tweets_ids'
REFERENCED_TWEETS_AUTHOR_IDS = 'referenced_tweets_authors'
REFERENCED_TWEETS_AUTHOR_USERNAMES = 'referenced_tweets_authors_usernames'
REPLY_SETTINGS = 'reply_settings'
SOURCE = 'source'
WITHHELD_COPYRIGHT = 'withheld_copyright'
WITHHELD_COUNTRY_CODES = 'withheld_country_codes'
WITHHELD_SCOPE = 'withheld_scope'
RULE_TAGS = 'rule_tags'

required_tweet_fields = {
    ID: 'id',
    TEXT: 'text',
    MEDIA_KEYS: 'attachments',
    MEDIA_SHA1S: 'attachments',
    MEDIA_FORMAT: 'attachments',
    MEDIA_TYPES: 'attachments',
    MEDIA_FILES: 'attachments',
    POLL_IDS: 'attachments',
    AUTHOR_ID: 'author_id',
    AUTHOR_USERNAME: 'author_id',
    CONTEXT_DOMAINS: 'context_annotations',
    CONTEXT_ENTITIES: 'context_annotations',
    CONVERSATION_ID: 'conversation_id',
    CREATED_AT: 'created_at',
    ANNOTATIONS: 'entities',
    CASHTAGS: 'entities',
    HASHTAGS: 'entities',
    MENTIONS: 'entities',
    URLS: 'entities',
    COORDINATES: 'geo',
    PLACE_ID: 'geo',
    IN_REPLY_TO_USER_ID: 'in_reply_to_user_id',
    IN_REPLY_TO_USERNAME: 'in_reply_to_user_id',
    LANG: 'lang',
    POSSIBLY_SENSITIVE: 'possibly_sensitive',
    RETWEET_COUNT: 'public_metrics',
    REPLY_COUNT: 'public_metrics',
    LIKE_COUNT: 'public_metrics',
    QUOTE_COUNT: 'public_metrics',
    REFERENCED_TWEETS_TYPES: 'referenced_tweets',
    REFERENCED_TWEETS_IDS: 'referenced_tweets',
    REFERENCED_TWEETS_AUTHOR_IDS: 'referenced_tweets',
    REFERENCED_TWEETS_AUTHOR_USERNAMES: 'referenced_tweets',
    REPLY_SETTINGS: 'reply_settings',
    SOURCE: 'source',
    WITHHELD_COPYRIGHT: 'withheld',
    WITHHELD_COUNTRY_CODES: 'withheld',
    WITHHELD_SCOPE: 'withheld',
    RULE_TAGS: 'id'
}

tweet_fields = list(required_tweet_fields.keys())


class TweetView2(DataView2):

    @staticmethod
    def get_fields() -> List[str]:
        return tweet_fields

    @staticmethod
    def get_default_fields() -> List[str]:
        return [ID, AUTHOR_USERNAME, CREATED_AT, TEXT, HASHTAGS]

    @classmethod
    def _compute(cls, tree: CollectionTree, fields: List[str], ids: List[str | int] = None, **kwargs) -> List[ViewDict]:
        res = []

        tweets = tree.get_tweets(ids)
        for tweet in tweets:
            res.append(cls._tweet_to_view(tweet, fields=fields))

        return res

    @classmethod
    def _tweet_to_view(cls, tweet_node: TweetNode, fields: List[str]):
        res = ViewDict(id_=tweet_node.id)

        safe_set = get_safe_set(res, fields)
        any_ = get_any_field(fields)

        tweet = tweet_node.data

        safe_set(ID, tweet.id)
        safe_set(TEXT, tweet.text)
        safe_set(CREATED_AT, tweet.created_at)
        safe_set(CONVERSATION_ID, tweet.conversation_id)

        if tweet.attachments and tweet.attachments.poll_ids:
            safe_set(POLL_IDS, tweet.attachments.poll_ids)

        author = tweet_node.author()
        if author:
            safe_set(AUTHOR_ID, author.id)
            safe_set(AUTHOR_USERNAME, author.data.username)

        if any_(CONTEXT_DOMAINS, CONTEXT_ENTITIES):
            if tweet.context_annotations:
                domains = [c.domain.name for c in tweet.context_annotations]
                entities = [c.entity.name for c in tweet.context_annotations]
                safe_set(CONTEXT_DOMAINS, domains)
                safe_set(CONTEXT_ENTITIES, entities)

        if tweet.entities:
            if tweet.entities.annotations:
                annotations = [a.normalized_text for a in tweet.entities.annotations]
                safe_set(ANNOTATIONS, annotations)
            if tweet.entities.cashtags:
                tags = [t.tag for t in tweet.entities.cashtags]
                safe_set(CASHTAGS, tags)
            if tweet.entities.hashtags:
                tags = [t.tag for t in tweet.entities.hashtags]
                safe_set(HASHTAGS, tags)
            if tweet.entities.mentions:
                mentions = [t.username for t in tweet.entities.mentions]
                safe_set(MENTIONS, mentions)
            if tweet.entities.urls:
                urls = [t.url for t in tweet.entities.urls]
                safe_set(URLS, urls)

        if tweet.geo:
            if tweet.geo.coordinates:
                safe_set(COORDINATES, tweet.geo.coordinates.coordinates)
            safe_set(PLACE_ID, tweet.geo.place_id)

        if tweet.in_reply_to_user_id:
            safe_set(IN_REPLY_TO_USER_ID, tweet.in_reply_to_user_id)
            # if tweet.in_reply_to_user_id in bulk_data.users:
            #     safe_set(IN_REPLY_TO_USERNAME, bulk_data.users[tweet.in_reply_to_user_id].username)

        safe_set(LANG, tweet.lang)
        safe_set(POSSIBLY_SENSITIVE, tweet.possibly_sensitive)

        if tweet.public_metrics:
            safe_set(RETWEET_COUNT, tweet.public_metrics.retweet_count)
            safe_set(REPLY_COUNT, tweet.public_metrics.reply_count)
            safe_set(LIKE_COUNT, tweet.public_metrics.like_count)
            safe_set(QUOTE_COUNT, tweet.public_metrics.quote_count)

        if tweet.referenced_tweets:
            tweet_types = [t.type for t in tweet.referenced_tweets]
            tweet_ids = [t.id for t in tweet.referenced_tweets]
            safe_set(REFERENCED_TWEETS_TYPES, tweet_types)
            safe_set(REFERENCED_TWEETS_IDS, tweet_ids)

            # if any_field(REFERENCED_TWEETS_AUTHOR_IDS, REFERENCED_TWEETS_AUTHOR_USERNAMES):
            #     tweets = [bulk_data.tweets[i] for i in tweet_ids if i in bulk_data.tweets]
            #     author_ids = [t.author_id for t in tweets if t.author_id]
            #     authors = [bulk_data.users[i] for i in author_ids if i in bulk_data.users]
            #     author_usernames = [a.username for a in authors if a.username]
            #
            #     safe_set(REFERENCED_TWEETS_AUTHOR_IDS, author_ids)
            #     safe_set(REFERENCED_TWEETS_AUTHOR_USERNAMES, author_usernames)

        safe_set(REPLY_SETTINGS, tweet.reply_settings)
        safe_set(SOURCE, tweet.source)

        if tweet.withheld:
            safe_set(WITHHELD_COPYRIGHT, tweet.withheld.copyright)
            safe_set(WITHHELD_SCOPE, tweet.withheld.scope)
            safe_set(WITHHELD_COUNTRY_CODES, tweet.withheld.country_codes)

        return res
