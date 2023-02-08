import asyncio
import time
from collections import defaultdict
from typing import List

from restweetution.collection import Collection
from restweetution.models.bulk_data import BulkData
from restweetution.models.event_data import BulkIds
from restweetution.models.extended_types import ExtendedTweet
from restweetution.models.rule import CollectedTweet
from restweetution.models.twitter import Tweet
from restweetution.storages.postgres_jsonb_storage.postgres_jsonb_storage import PostgresJSONBStorage


def get_media_keys_from_tweet(tweet: Tweet):
    if tweet.attachments and tweet.attachments.media_keys:
        return tweet.attachments.media_keys
    return []


def get_media_keys_from_tweets(tweets: List[Tweet]):
    res = [get_media_keys_from_tweet(t) for t in tweets]
    res = [k for k in res if k]
    return res


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

    async def expand_collected_tweets(self, collected: List[CollectedTweet]):
        data = BulkData()

        if not collected:
            return data

        rule_ids = {c.rule_id for c in collected}
        rule_ids = list(rule_ids)
        rules = await self.storage.get_rules(ids=rule_ids)
        data.add_rules(rules)
        data.add_collected_tweets(collected)

        tweets = [c.tweet for c in collected]
        # find ids of objects (tweets, media, polls, etc..) referenced by the tweets
        ref_ids = sum((get_ids_from_tweet(t) for t in tweets), BulkIds())

        # print(f'Extract: tweets: {len(ref_ids.tweets)}, users: {len(ref_ids.users)}, medias: {len(ref_ids.medias)} ...')

        # utility function to be awaited later with asyncio.gather
        # the function awaits the get request to the database and uses a given function to save the result
        async def get_and_save(get_func, save_func):
            res = await get_func
            save_func(res)

        # list of tasks to be gathered later
        tasks = []
        if ref_ids.tweets:
            tasks.append(get_and_save(self.storage.get_collected_tweets(ids=list(ref_ids.tweets), rule_ids=rule_ids),
                                      data.add_collected_tweets))
        if ref_ids.users:
            tasks.append(get_and_save(self.storage.get_users(ids=list(ref_ids.users)), data.add_users))
        if ref_ids.polls:
            tasks.append(get_and_save(self.storage.get_polls(ids=list(ref_ids.polls)), data.add_polls))
        if ref_ids.places:
            tasks.append(get_and_save(self.storage.get_places(ids=list(ref_ids.places)), data.add_places))
        if ref_ids.medias:
            tasks.append(get_and_save(self.storage.get_medias(media_keys=list(ref_ids.medias)), data.add_medias))

        await asyncio.gather(*tasks)

        if data.medias:
            res_downloaded = await self.storage.get_downloaded_medias(media_keys=list(ref_ids.medias))
            for r in res_downloaded:
                r.media = data.medias[r.media_key]
            data.add_downloaded_medias(res_downloaded)

        return data

    async def add_users_from_tweets(self, collection: Collection, tweets: List[ExtendedTweet]):
        pass

    async def add_medias_from_tweets(self, collection: Collection, tweets: List[ExtendedTweet]):
        media_to_tweets = defaultdict(list)
        for t in tweets:
            for m in t.tweet.media_keys():
                media_to_tweets[m].append(t.id)

        media_keys = list(media_to_tweets.keys())
        if not media_keys:
            return
        res = await self.storage.get_extended_medias(media_keys=media_keys, tweet_ids=False, downloaded=True)
        for r in res:
            r.tweet_ids = media_to_tweets[r.media_key]
        collection.add_medias(res)

    async def add_rules_from_tweets(self, collection: Collection, tweets: List[ExtendedTweet]):
        rule_to_collected = defaultdict(list)
        for t in tweets:
            for collected in t.sources:
                rule_to_collected[collected.rule_id].append(collected)

        rule_ids = list(rule_to_collected.keys())
        if not rule_ids:
            return
        res = await self.storage.get_rules(ids=rule_ids)
        for rule in res:
            for collected in rule_to_collected[rule.id]:
                rule.collected_tweets[collected.tweet_id] = collected

        collection.add_rules(res)

    async def collection_from_tweets(self, tweets: List[ExtendedTweet]):
        collection = Collection()
        collection.add_tweets(tweets)

        media_task = self.add_medias_from_tweets(collection, tweets)
        rule_task = self.add_rules_from_tweets(collection, tweets)

        await asyncio.gather(media_task, rule_task)

        return collection
