import asyncio
import time
from collections import defaultdict
from typing import List, Callable

from restweetution.collection import Collection
from restweetution.models.bulk_data import BulkData
from restweetution.models.event_data import BulkIds
from restweetution.models.extended_types import ExtendedTweet
from restweetution.models.linked.linked_tweet import LinkedTweet
from restweetution.models.rule import RuleMatch
from restweetution.models.storage.downloaded_media import DownloadedMedia
from restweetution.models.twitter import Tweet, Media
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
        self._loaded = BulkIds()

    async def expand_collected_tweets(self, collected: List[RuleMatch]):
        data = BulkData()

        if not collected:
            return data

        rule_ids = {c.rule_id for c in collected}
        rule_ids = list(rule_ids)
        rules = await self.storage.get_rules(ids=rule_ids)
        data.add_rules(rules)
        data.add_rule_matches(collected)

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
                                      data.add_rule_matches))
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
        # TODO: write expansion code.
        # TODO: remember every id link to user (author_of, mention_by, replied_by)
        pass

    async def add_medias_from_tweets(self, collection: Collection, tweets: List[ExtendedTweet]):
        media_to_tweets = defaultdict(list)
        for t in tweets:
            for m in t.tweet.get_media_keys():
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
                rule.matches[collected.tweet_id] = collected

        collection.add_rules(res)

    async def collection_from_tweets(self, tweets: List[ExtendedTweet]):
        collection = Collection()
        collection.add_tweets(tweets)

        media_task = self.add_medias_from_tweets(collection, tweets)
        rule_task = self.add_rules_from_tweets(collection, tweets)

        await asyncio.gather(media_task, rule_task)

        return collection

    async def tweet_load_medias(self, tweets: List[LinkedTweet]):
        if not tweets:
            return []
        data = tweets[0].data

        media_keys = []
        [media_keys.extend(t.tweet.get_media_keys()) for t in tweets]
        media_keys = [m for m in media_keys if m and m not in self._loaded.medias]

        if not media_keys:
            return []
        self._loaded.medias.update(media_keys)

        get_medias = self.storage.get_medias(media_keys=media_keys)
        get_downloaded_medias = self.storage.get_downloaded_medias(media_keys=media_keys)

        medias, d_medias = await asyncio.gather(get_medias, get_downloaded_medias)
        medias: List[Media]
        d_medias: List[DownloadedMedia]

        data.add_medias(medias)
        for d_media in d_medias:
            d_media.media = data.medias[d_media.media_key]
        data.add_downloaded_medias(d_medias)

        loaded = []
        loaded.extend(medias)
        loaded.extend(d_medias)
        return loaded

    async def tweet_load_polls(self, tweets: List[LinkedTweet]):
        if not tweets:
            return []
        data = tweets[0].data

        poll_ids = []
        [poll_ids.extend(t.tweet.get_poll_ids()) for t in tweets]
        poll_ids = [p for p in poll_ids if p and p not in self._loaded.polls]
        if not poll_ids:
            return []
        self._loaded.polls.update(poll_ids)

        polls = await self.storage.get_polls(ids=poll_ids)
        data.add_polls(polls)
        return polls

    async def tweet_load_author_user(self, tweets: List[LinkedTweet]):
        if not tweets:
            return []
        data = tweets[0].data

        user_ids = [t.tweet.author_id for t in tweets if t.tweet.author_id]
        user_ids = [u for u in user_ids if u and u not in self._loaded.users]
        if not user_ids:
            return []
        self._loaded.users.update(user_ids)

        users = await self.storage.get_users(ids=user_ids)
        data.add_users(users)
        return users

    async def tweet_load_replied_user(self, tweets: List[LinkedTweet]):
        if not tweets:
            return []
        data = tweets[0].data

        user_ids = [t.tweet.in_reply_to_user_id for t in tweets]
        user_ids = [u for u in user_ids if u and u not in self._loaded.users]
        if not user_ids:
            return []
        self._loaded.users.update(user_ids)

        users = await self.storage.get_users(ids=user_ids)
        data.add_users(users)
        return users

    async def tweet_load_users(self, tweets: List[LinkedTweet]):
        if not tweets:
            return

        loaded = []
        res = await asyncio.gather(
            self.tweet_load_replied_user(tweets),
            self.tweet_load_author_user(tweets)
        )
        [loaded.extend(r) for r in res]
        return loaded

    async def tweet_load_replied_tweet(self, tweets: List[LinkedTweet]):
        return await self.tweet_load_tweet(tweets, id_fn=lambda t: t.tweet.get_replied_to_id())

    async def tweet_load_retweeted_tweet(self, tweets: List[LinkedTweet]):
        return await self.tweet_load_tweet(tweets, id_fn=lambda t: t.tweet.get_retweeted_id())

    async def tweet_load_quoted_tweet(self, tweets: List[LinkedTweet]):
        return await self.tweet_load_tweet(tweets, id_fn=lambda t: t.tweet.get_quoted_id())

    async def tweet_load_conversation_tweet(self, tweets: List[LinkedTweet]):
        return await self.tweet_load_tweet(tweets, id_fn=lambda t: t.tweet.conversation_id)

    async def tweet_load_referenced_tweets(self, tweets: List[LinkedTweet]):
        loaded = []
        retweeted, replied, quoted, conv = await asyncio.gather(
            self.tweet_load_retweeted_tweet(tweets),
            self.tweet_load_replied_tweet(tweets),
            self.tweet_load_quoted_tweet(tweets),
            self.tweet_load_conversation_tweet(tweets)
        )
        [loaded.extend(t) for t in [retweeted, replied, quoted, conv] if t]
        return loaded

    async def tweet_load_tweet(self, tweets: List[LinkedTweet], id_fn: Callable):
        if not tweets:
            return []
        data = tweets[0].data
        self._loaded.tweets.update([t.tweet.id for t in tweets])

        tweet_ids = list({id_fn(t) for t in tweets})
        tweet_ids = [t for t in tweet_ids if t and t not in self._loaded.tweets]
        # print(tweet_ids)
        self._loaded.tweets.update(tweet_ids)
        if not tweet_ids:
            return []

        tweet_res = await self.storage.get_tweets(ids=tweet_ids)
        # print('search tweet_ids len: ', len(tweet_ids))
        # print('find tweet_ids len: ', len(tweet_res))

        data.add_tweets(tweet_res)
        linked_tweets = data.get_linked_tweets([t.id for t in tweet_res])
        return linked_tweets

    async def tweet_load_all(self, tweets: List[LinkedTweet]):
        res = await asyncio.gather(
            self.tweet_load_referenced_tweets(tweets),
            self.tweet_load_users(tweets),
            self.tweet_load_medias(tweets),
            self.tweet_load_polls(tweets)
        )
        return res
