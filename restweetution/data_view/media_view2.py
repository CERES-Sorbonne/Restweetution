from typing import List

from restweetution.collection import CollectionTree, MediaNode
from restweetution.data_view.data_view2 import DataView2, get_safe_set, ViewDict
from restweetution.data_view.fields import MediaFields as MEDIA


class MediaView2(DataView2):
    @staticmethod
    def get_fields() -> List[str]:
        return [MEDIA.MEDIA_KEY, MEDIA.TYPE, MEDIA.SHA1, MEDIA.FORMAT, MEDIA.FILE]

    @staticmethod
    def get_default_fields() -> List[str]:
        return [MEDIA.MEDIA_KEY, MEDIA.TYPE, MEDIA.FILE]

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
        safe_set(MEDIA.MEDIA_KEY, m.media_key)
        safe_set(MEDIA.TYPE, m.type)

        dm = media.downloaded
        if dm:
            safe_set(MEDIA.SHA1, dm.sha1)
            safe_set(MEDIA.FORMAT, dm.format)
            safe_set(MEDIA.FILE, dm.sha1 + '.' + dm.format)

        return res
