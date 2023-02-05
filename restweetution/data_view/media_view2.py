from abc import ABC
from typing import List

from restweetution.collection import CollectionTree, MediaNode
from restweetution.data_view.data_view2 import DataView2, get_safe_set, ViewDict

MEDIA_KEY = 'media_key'
MEDIA_TYPE = 'media_type'

MEDIA_SHA1 = 'media_sha1'
MEDIA_FILE = 'media_file'
MEDIA_FORMAT = 'media_format'

RULE_TAGS = 'rule_tags'


class MediaView2(DataView2, ABC):
    @staticmethod
    def get_fields() -> List[str]:
        return [MEDIA_KEY, MEDIA_TYPE, MEDIA_SHA1, MEDIA_FORMAT, MEDIA_FORMAT, RULE_TAGS]

    @staticmethod
    def get_default_fields() -> List[str]:
        return [MEDIA_KEY, MEDIA_TYPE, MEDIA_FILE]

    @classmethod
    def _compute(cls, tree: CollectionTree, fields: List[str], ids: List[str | int] = None, **kwargs) -> List[ViewDict]:
        tweets = tree.get_tweets(tweet_ids=ids)
        res = []

        for tweet in tweets:
            for media in tweet.medias():
                res.append(cls._compute_media(media, fields))

        return res

    @staticmethod
    def _compute_media(media: MediaNode, fields: List[str]):
        res = ViewDict(id_=media.id)

        safe_set = get_safe_set(res, fields)

        m = media.data
        safe_set(MEDIA_KEY, m.media_key)
        safe_set(MEDIA_TYPE, m.type)

        dm = media.downloaded
        if dm:
            safe_set(MEDIA_SHA1, dm.sha1)
            safe_set(MEDIA_FORMAT, dm.format)
            safe_set(MEDIA_FILE, dm.sha1 + '.' + dm.format)

        rule_tags = set()
        for r in media.rules():
            rule_tags.update(r.data.tag.split(','))
        safe_set(RULE_TAGS, list(rule_tags))

        return res
