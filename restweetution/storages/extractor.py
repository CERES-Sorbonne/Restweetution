from typing import List

from restweetution.models.bulk_data import BulkData
from restweetution.models.event_data import BulkIds
from restweetution.models.twitter import Tweet
from restweetution.storages.postgres_jsonb_storage.postgres_jsonb_storage import PostgresJSONBStorage


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
    def __init__(self, storage: PostgresJSONBStorage):
        self.storage = storage

    async def expand_tweets(self, tweets: List[Tweet]):
        data = BulkData()
        data.add_tweets(tweets)

        ids = sum((get_ids_from_tweet(t) for t in tweets), BulkIds())

        res_tweets = await self.storage.get_tweets(ids=list(ids.tweets))
        data.add_tweets(res_tweets)

        res_users = await self.storage.get_users(ids=list(ids.users))
        data.add_users(res_users)

        res_polls = await self.storage.get_polls(ids=list(ids.polls))
        data.add_polls(res_polls)

        res_places = await self.storage.get_places(ids=list(ids.places))
        data.add_places(res_places)

        res_medias = await self.storage.get_medias(media_keys=list(ids.medias))
        data.add_medias(res_medias)

        res_downloaded = await self.storage.get_downloaded_medias(media_keys=[r.media_key for r in res_medias])
        for r in res_downloaded:
            r.media = data.medias[r.media_key]

        data.add_downloaded_medias(res_downloaded)

        res_rule = await self.storage.get_rule_with_collected_tweets(tweet_ids=[t.id for t in data.get_tweets()])
        data.add_rules(res_rule)

        return data



