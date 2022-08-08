from typing import List, Tuple

from restweetution.models.bulk_data import BulkData
from restweetution.models.event_data import BulkIds
from restweetution.models.twitter import Tweet


def get_ids_from_tweet(tweet: Tweet):
    ids = BulkIds()

    if tweet.attachments and tweet.attachments.media_keys:
        ids.medias.update(tweet.attachments.media_keys)
    if tweet.attachments and tweet.attachments.poll_ids:
        ids.polls.update(tweet.attachments.poll_ids)
    if tweet.author_id:
        ids.users.add(tweet.author_id)
    if tweet.conversation_id:
        ids.tweets.add(tweet.conversation_id)
    if tweet.geo and tweet.geo.place_id:
        ids.places.add(tweet.geo.place_id)
    if tweet.in_reply_to_user_id:
        ids.users.add(tweet.in_reply_to_user_id)
    if tweet.referenced_tweets:
        ids.tweets.update([t.id for t in tweet.referenced_tweets])

    return ids


class Extractor:
    def __init__(self, storage):
        self.storage = storage

    async def get_tweets(self, expand: List[str] = None, fields=None, **kwargs) -> Tuple[BulkData, List[Tweet]]:
        bulk_data = BulkData()
        tweets = await self.storage.get_tweets(**kwargs)
        bulk_data.add_tweets(tweets)

        if expand:
            ids = sum([get_ids_from_tweet(t) for t in tweets], BulkIds())

            if 'tweet' in expand:
                tw = await self.storage.get_tweets(fields=fields, ids=ids.tweets)
                bulk_data.add_tweets(tw)
            if 'user' in expand:
                us = await self.storage.get_users(fields=fields, ids=ids.users)
                bulk_data.add_users(us)
            if 'poll' in expand:
                us = await self.storage.get_polls(fields=fields, ids=ids.polls)
                bulk_data.add_polls(us)
            if 'place' in expand:
                us = await self.storage.get_places(fields=fields, ids=ids.places)
                bulk_data.add_places(us)
            if 'media' in expand:
                us = await self.storage.get_medias(fields=fields, ids=ids.medias)
                bulk_data.add_medias(us)
        return bulk_data, tweets


