from collections import defaultdict
from typing import List, Dict

from restweetution.data_view.data_view import DataView
from restweetution.data_view.tweet_view import TweetView
from restweetution.models.bulk_data import BulkData
from restweetution.models.twitter import Tweet, Media
from restweetution.storages.extractor import get_media_keys_from_tweets, get_media_keys_from_tweet

MEDIA_KEY = 'media_key'
MEDIA_TYPE = 'media_type'

MEDIA_SHA1 = 'media_sha1'
MEDIA_FILE = 'media_file'
MEDIA_FORMAT = 'media_format'

TWEET_ID = 'tweet_id'
TWEET_TEXT = 'tweet_text'
TWEET_CREATED_AT = 'tweet_created_at'

AUTHOR_ID = 'author_id'
AUTHOR_USERNAME = 'author_username'
CONTEXT_DOMAIN = 'context_domains'
CONTEXT_ENTITIES = 'context_entities'
CONVERSATION_ID = 'conversation_id'

ANNOTATIONS = 'annotations'
CASHTAGS = 'cashtags'
HASHTAGS = 'hashtags'
MENTIONS = 'mentions'
# URLS = 'urls'
COORDINATES = 'coordinates'
PLACE_ID = 'place_id'
IN_REPLY_TO_USER_ID = 'in_reply_to_user_id'
IN_REPLY_TO_USERNAME = 'in_reply_to_username'
LANG = 'lang'
POSSIBLY_SENSITIVE = 'possibly_sensitive'
# RETWEET_COUNT = 'retweet_count'
# REPLY_COUNT = 'reply_count'
# LIKE_COUNT = 'like_count'
# QUOTE_COUNT = 'quote_count'
# REFERENCED_TWEETS_TYPES = 'referenced_tweets_types'
# REFERENCED_TWEETS_IDS = 'referenced_tweets_ids'
# REFERENCED_TWEETS_AUTHOR_IDS = 'referenced_tweets_authors'
# REFERENCED_TWEETS_AUTHOR_USERNAMES = 'referenced_tweets_authors_usernames'
REPLY_SETTINGS = 'reply_settings'
SOURCE = 'source'
WITHHELD_COPYRIGHT = 'withheld_copyright'
WITHHELD_COUNTRY_CODES = 'withheld_country_codes'
WITHHELD_SCOPE = 'withheld_scope'
RULE_TAGS = 'rule_tags'

media_fields = [
    MEDIA_KEY,
    MEDIA_SHA1,
    MEDIA_FORMAT,
    MEDIA_TYPE,
    MEDIA_FILE,
    TWEET_ID,
    TWEET_TEXT,
    TWEET_CREATED_AT,
    AUTHOR_ID,
    AUTHOR_USERNAME,
    CONTEXT_DOMAIN,
    CONTEXT_ENTITIES,
    CONVERSATION_ID,
    ANNOTATIONS,
    CASHTAGS,
    HASHTAGS,
    MENTIONS,
    COORDINATES,
    PLACE_ID,
    IN_REPLY_TO_USER_ID,
    IN_REPLY_TO_USERNAME,
    LANG,
    POSSIBLY_SENSITIVE,
    REPLY_SETTINGS,
    SOURCE,
    WITHHELD_COPYRIGHT,
    WITHHELD_COUNTRY_CODES,
    WITHHELD_SCOPE,
    RULE_TAGS,
]


tweet_fields = [
    'id',
    'text',
    'created_at',
    AUTHOR_ID,
    AUTHOR_USERNAME,
    CONTEXT_DOMAIN,
    CONTEXT_ENTITIES,
    CONVERSATION_ID,
    ANNOTATIONS,
    CASHTAGS,
    HASHTAGS,
    MENTIONS,
    COORDINATES,
    PLACE_ID,
    IN_REPLY_TO_USER_ID,
    IN_REPLY_TO_USERNAME,
    LANG,
    POSSIBLY_SENSITIVE,
    REPLY_SETTINGS,
    SOURCE,
    WITHHELD_COPYRIGHT,
    WITHHELD_COUNTRY_CODES,
    WITHHELD_SCOPE,
    RULE_TAGS,
]


class MediaView(DataView):
    @staticmethod
    def id_field() -> str:
        return 'id'

    @staticmethod
    # def get_required_fields(fields: List[str]):
    #     res = {required_tweet_fields[f] for f in fields}
    #     return list(res)

    @staticmethod
    def compute(bulk_data: BulkData, only_ids: List[str] = None, fields: List[str] = None):
        if not fields:
            fields = media_fields.copy()

        datas = []
        tweets = [bulk_data.tweets[i] for i in only_ids] if only_ids else bulk_data.get_tweets()

        media_to_tweets = defaultdict(list)
        for tweet in tweets:
            media_keys = get_media_keys_from_tweet(tweet)
            for k in media_keys:
                media_to_tweets[k].append(tweet)

        medias = [bulk_data.medias[k] for k in media_to_tweets.keys() if k in bulk_data.medias]
        for m in medias:
            datas.append(MediaView._media_to_row(m, bulk_data, dict(media_to_tweets), fields=fields))

        return datas

    @staticmethod
    def _media_to_row(media: Media, bulk_data: BulkData, media_to_tweets: Dict[str, List[Tweet]], fields: List[str]):
        data = {}

        for k in fields:
            data[k] = None

        def safe_set(field, value):
            if field in fields:
                data[field] = value

        def any_field(*field_list):
            return any(f in fields for f in field_list)

        safe_set(MEDIA_KEY, media.media_key)
        safe_set(MEDIA_TYPE, media.type)

        if media.media_key in bulk_data.downloaded_medias:
            d = bulk_data.downloaded_medias[media.media_key]
            safe_set(MEDIA_SHA1, d.sha1)
            safe_set(MEDIA_FILE, d.sha1 + '.' + d.format)
            safe_set(MEDIA_FORMAT, d.format)

        tweets = media_to_tweets[media.media_key]
        if not tweets:
            return data

        tweet_datas = TweetView.compute(bulk_data=bulk_data, only_ids=[t.id for t in tweets], fields=tweet_fields)
        final_data = {}
        for k in tweet_datas[0]:
            final_data[k] = list()
        for d in tweet_datas:
            for k in d:
                if not d[k]:
                    continue
                if isinstance(d[k], list):
                    final_data[k].extend(d[k])
                else:
                    final_data[k].append(d[k])
        # for k in final_data:
        #     final_data[k] = list(final_data[k])

        final_data[TWEET_ID] = final_data['id']
        final_data[TWEET_TEXT] = final_data['text']
        final_data[TWEET_CREATED_AT] = final_data['created_at']

        for f in media_fields:
            if f in final_data:
                data[f] = final_data[f]

        return data
