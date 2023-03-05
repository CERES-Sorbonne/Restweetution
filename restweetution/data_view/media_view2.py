from typing import List

from restweetution.collection import CollectionTree, MediaNode
from restweetution.data_view.data_view2 import DataView2, get_safe_set, ViewDict
from restweetution.data_view.fields import MediaFields as MEDIA
from restweetution.models.linked.linked_media import LinkedMedia


class MediaView2(DataView2):
    @staticmethod
    def get_fields() -> List[str]:
        return [MEDIA.MEDIA_KEY, MEDIA.TYPE, MEDIA.SHA1, MEDIA.FORMAT, MEDIA.FILE]

    @staticmethod
    def get_default_fields() -> List[str]:
        return [MEDIA.MEDIA_KEY, MEDIA.TYPE, MEDIA.FILE]

    @classmethod
    def compute(cls, medias: List[LinkedMedia], fields: List[str] = None) -> List[ViewDict]:
        fields = cls.all_if_empty(fields)
        res = []

        for media in medias:
            res.append(cls._compute_media(media, fields))

        return res

    @staticmethod
    def _compute_media(linked_media: LinkedMedia, fields: List[str]):
        media = linked_media.media
        downloaded = linked_media.downloaded
        res = ViewDict(id_=media.media_key)

        safe_set = get_safe_set(res, fields)

        safe_set(MEDIA.MEDIA_KEY, media.media_key)
        safe_set(MEDIA.TYPE, media.type)

        if downloaded:
            safe_set(MEDIA.SHA1, downloaded.sha1)
            safe_set(MEDIA.FORMAT, downloaded.format)
            safe_set(MEDIA.FILE, downloaded.sha1 + '.' + downloaded.format)

        return res
