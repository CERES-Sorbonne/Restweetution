from typing import List

from restweetution.data_view.data_view2 import DataView2, get_safe_set, ViewDict, ViewResult
from restweetution.data_view.fields import MediaFields as MField
from restweetution.data_view.fields import TweetFields as TField
from restweetution.models.linked.linked_media import LinkedMedia


class MediaView2(DataView2):
    @staticmethod
    def get_fields() -> List[str]:
        return [
            MField.MEDIA_KEY, MField.TYPE, MField.SHA1, MField.FORMAT, MField.FILE,
            TField.ID, TField.TEXT, TField.AUTHOR_ID,
        ]

    @staticmethod
    def get_default_fields() -> List[str]:
        return [MField.MEDIA_KEY, MField.TYPE, MField.FILE]

    @classmethod
    def compute(cls, medias: List[LinkedMedia], fields: List[str] = None) -> ViewResult:
        fields = cls.all_if_empty(fields)
        res = []

        for MField in medias:
            res.append(cls._compute_media(MField, fields))

        return cls._result(view_list=res, fields=fields)

    @staticmethod
    def _compute_media(linked_media: LinkedMedia, fields: List[str]):
        media = linked_media.media
        downloaded = linked_media.downloaded

        res = ViewDict(id_=media.media_key)

        safe_set = get_safe_set(res, fields)

        safe_set(MField.MEDIA_KEY, media.media_key)
        safe_set(MField.TYPE, media.type)

        if downloaded:
            safe_set(MField.SHA1, downloaded.sha1)
            safe_set(MField.FORMAT, downloaded.format)
            safe_set(MField.FILE, downloaded.sha1 + '.' + downloaded.format)

        tweets = linked_media.get_tweets()
        if tweets:
            safe_set(TField.ID, [t.tweet.id for t in tweets])
            safe_set(TField.TEXT, [t.tweet.text for t in tweets])
            safe_set(TField.AUTHOR_ID, [t.tweet.author_id for t in tweets])

        return res
