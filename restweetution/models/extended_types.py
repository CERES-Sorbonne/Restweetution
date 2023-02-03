from typing import List

from pydantic import BaseModel

from restweetution.models.rule import CollectedTweet
from restweetution.models.storage.downloaded_media import DownloadedMedia
from restweetution.models.twitter import Media, Tweet


class ExtendedTweet(BaseModel):
    id: str
    tweet: Tweet
    sources: List[CollectedTweet] = []

    def __init__(self, tweet: Tweet, **kwargs):
        super().__init__(tweet=tweet, id=tweet.id, **kwargs)


class ExtendedMedia(BaseModel):
    media: Media
    media_key: str
    downloaded: DownloadedMedia = None
    tweet_ids: List[str] = []

    def __init__(self, media: Media, **kwargs):
        super().__init__(media=media, media_key=media.media_key, **kwargs)
