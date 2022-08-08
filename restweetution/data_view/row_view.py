from typing import List

from restweetution.data_view.data_view import DataView
from restweetution.models.bulk_data import BulkData
from restweetution.models.storage.custom_data import CustomData
from restweetution.models.twitter import Tweet
from restweetution.storages.extractor import Extractor

ID = 'id'
TEXT = 'text'
MEDIA_KEYS = 'media_keys'
MEDIA_SHA1S = 'media_sha1s'
MEDIA_TYPES = 'media_types'
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
REPLY_SETTINGS = 'reply_settings'
SOURCE = 'source'
WITHHELD_COPYRIGHT = 'withheld_copyright'
WITHHELD_COUNTRY_CODES = 'withheld_country_codes'
WITHHELD_SCOPE = 'withheld_scope'

tweet_fields = [
    ID,
    TEXT,
    MEDIA_KEYS,
    MEDIA_SHA1S,
    MEDIA_TYPES,
    POLL_IDS,
    AUTHOR_ID,
    AUTHOR_USERNAME,
    CONTEXT_DOMAINS,
    CONTEXT_ENTITIES,
    CONVERSATION_ID,
    CREATED_AT,
    ANNOTATIONS,
    CASHTAGS,
    HASHTAGS,
    MENTIONS,
    URLS,
    COORDINATES,
    PLACE_ID,
    IN_REPLY_TO_USER_ID,
    IN_REPLY_TO_USERNAME,
    LANG,
    POSSIBLY_SENSITIVE,
    RETWEET_COUNT,
    REPLY_COUNT,
    LIKE_COUNT,
    QUOTE_COUNT,
    REFERENCED_TWEETS_TYPES,
    REFERENCED_TWEETS_IDS,
    REPLY_SETTINGS,
    SOURCE,
    WITHHELD_COPYRIGHT,
    WITHHELD_COUNTRY_CODES,
    WITHHELD_SCOPE
]


class RowView(DataView):
    def __init__(self, in_storage, out_storage, fields=None):
        if not fields:
            fields = tweet_fields.copy()
        for f in fields:
            if f not in tweet_fields:
                raise ValueError(f'{f} is not a supported field\nValid fields: {tweet_fields}')
        self.fields = fields
        super().__init__(name='flat_view', in_storage=in_storage, out_storage=out_storage)

    async def load(self):
        extractor = Extractor(self.input)
        bulk_data, tweets = await extractor.get_tweets(expand=['tweet', 'user', 'media', 'place', 'poll'])

        fields = self.fields

        rows = []
        for tweet in tweets:
            rows.append(self.tweet_to_row(tweet, bulk_data, fields))
            print(rows[-1].data)

        return rows

    async def save_rows(self, rows: List[CustomData]):
        await self.output.save_custom_datas(rows)

    @staticmethod
    def tweet_to_row(tweet: Tweet, bulk_data: BulkData, fields: List[str]):
        row = CustomData(key='tweet', id=tweet.id)
        data = row.data

        for k in fields:
            data[k] = None

        def safe_set(key, value):
            if key in fields:
                data[key] = value

        def any_field(field_list):
            return any(key in fields for key in field_list)

        safe_set(ID, tweet.id)
        safe_set(TEXT, tweet.text)

        if any_field([MEDIA_KEYS, MEDIA_SHA1S, MEDIA_TYPES]):
            if tweet.attachments and tweet.attachments.media_keys:
                keys = tweet.attachments.media_keys
                safe_set(MEDIA_KEYS, keys)

                medias = [bulk_data.medias[k] for k in keys if k in bulk_data.medias]
                sha1_list = [m.sha1 for m in medias if m.sha1]
                type_list = [m.type for m in medias if m.type]

                safe_set(MEDIA_SHA1S, sha1_list)
                safe_set(MEDIA_TYPES, type_list)
        if tweet.attachments and tweet.attachments.poll_ids:
            safe_set(POLL_IDS, tweet.attachments.poll_ids)

        safe_set(AUTHOR_ID, tweet.author_id)
        if tweet.author_id and tweet.author_id in bulk_data.users:
            safe_set(AUTHOR_USERNAME, bulk_data.users[tweet.author_id].username)
        if any_field([CONTEXT_DOMAINS, CONTEXT_ENTITIES]):
            if tweet.context_annotations:
                domains = [c.domain.name for c in tweet.context_annotations]
                entities = [c.entity.name for c in tweet.context_annotations]
                safe_set(CONTEXT_DOMAINS, domains)
                safe_set(CONTEXT_ENTITIES, entities)
        safe_set(CONVERSATION_ID, tweet.conversation_id)
        safe_set(CREATED_AT, tweet.created_at)

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
            if tweet.in_reply_to_user_id in bulk_data.users:
                safe_set(IN_REPLY_TO_USERNAME, bulk_data.users[tweet.in_reply_to_user_id].username)

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

        safe_set(REPLY_SETTINGS, tweet.reply_settings)
        safe_set(SOURCE, tweet.source)

        if tweet.withheld:
            safe_set(WITHHELD_COPYRIGHT, tweet.withheld.copyright)
            safe_set(WITHHELD_SCOPE, tweet.withheld.scope)
            safe_set(WITHHELD_COUNTRY_CODES, tweet.withheld.country_codes)

        return row
