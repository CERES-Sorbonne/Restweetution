from restweetution.models.linked.linked import Linked
from restweetution.models.twitter import Media


class LinkedMedia(Linked):
    def __init__(self, data, media: Media):
        super().__init__(data)
        self.media = media

        downloaded = self.data.downloaded_medias.get(media.media_key)
        self.downloaded = downloaded

    def get_tweets(self):
        tweet_ids = list(self.data.media_to_tweets[self.media.media_key])
        if not tweet_ids:
            return []
        return self.data.get_linked_tweets(tweet_ids=tweet_ids)
