import asyncio
from typing import Callable
from typing import List

from restweetution.models.event_data import BulkIds
from restweetution.models.linked.linked_bulk_data import LinkedBulkData
from restweetution.models.linked.linked_tweet import LinkedTweet
from restweetution.models.storage.queries import CollectionQuery, TweetFilter
from restweetution.storages.postgres_jsonb_storage.postgres_jsonb_storage import PostgresJSONBStorage


class StorageCollection:
    def __init__(self, storage: PostgresJSONBStorage, linked_data: LinkedBulkData = None):
        self._storage = storage

        if not linked_data:
            linked_data = LinkedBulkData()
        self.data = linked_data
        self.loaded = BulkIds()

        self._populate_loaded()

    def _populate_loaded(self):
        self.loaded.rules.update(self.data.rules.keys())
        self.loaded.users.update(self.data.users.keys())
        self.loaded.tweets.update(self.data.tweets.keys())
        self.loaded.places.update(self.data.places.keys())
        self.loaded.medias.update(self.data.medias.keys())
        self.loaded.polls.update(self.data.polls.keys())

    '''
    Base functions for loading from storage
    Use those to avoid double loading of same objects
    '''

    async def load_rules(self, ids: List[int]):
        if not ids:
            return []
        ids = self.loaded.only_new_rules(ids)
        if not ids:
            return []

        rules = await self._storage.get_rules(ids=ids)
        self.loaded.rules.update(ids)
        self.data.add_rules(rules)
        return rules

    async def load_users(self, ids: List[str]):
        if not ids:
            return []
        ids = self.loaded.only_new_users(ids)
        if not ids:
            return []

        users = await self._storage.get_users(ids=ids)
        self.loaded.users.update(ids)
        self.data.add_users(users)
        return users

    async def load_tweets(self, ids: List[str]):
        if not ids:
            return []
        ids = self.loaded.only_new_tweets(ids)
        if not ids:
            return []

        tweets = await self._storage.get_tweets(ids=ids)
        self.loaded.tweets.update(ids)
        self.data.add_tweets(tweets)
        return tweets

    async def load_places(self, ids: List[str]):
        if not ids:
            return []
        ids = self.loaded.only_new_places(ids)
        if not ids:
            return []

        places = await self._storage.get_places(ids=ids)
        self.loaded.places.update(ids)
        self.data.add_places(places)
        return places

    async def load_medias(self, media_keys: List[str]):
        if not media_keys:
            return []
        media_keys = self.loaded.only_new_medias(media_keys)
        if not media_keys:
            return []

        medias = await self._storage.get_medias(media_keys=media_keys)
        d_medias = await self._storage.get_downloaded_medias(media_keys=media_keys)

        self.loaded.medias.update(media_keys)
        self.data.add_medias(medias)

        for d in d_medias:
            d.media = self.data.medias[d.media_key]
        self.data.add_downloaded_medias(d_medias)

        linked_medias = self.data.get_linked_medias([m.media_key for m in medias])
        return linked_medias

    async def load_polls(self, ids: List[str]):
        if not ids:
            return []
        ids = self.loaded.only_new_polls(ids)
        if not ids:
            return []

        polls = await self._storage.get_polls(ids=ids)
        self.loaded.polls.update(ids)
        self.data.add_polls(polls)
        return polls

    '''
    Base functions to query certain objects with a CollectionQuery
    '''

    async def load_tweet_from_query(self, query: CollectionQuery):
        tweets, matches = await self._storage.get_tweets2(query)

        self.data.add_tweets(tweets)
        tweet_ids = [t.id for t in tweets]
        self.loaded.tweets.update(tweet_ids)

        rule_ids = list({m.rule_id for m in matches})
        await self.load_rules(rule_ids)
        self.data.add_rule_matches(matches)

        res_tweets = self.data.get_linked_tweets(tweet_ids)
        return res_tweets

    async def load_media_from_query(self, query: CollectionQuery):
        tweets, matches = await self._storage.get_tweets2(query, TweetFilter(media=True))

        self.data.add_tweets(tweets)
        tweet_ids = [t.id for t in tweets]
        self.loaded.tweets.update(tweet_ids)

        rule_ids = list({m.rule_id for m in matches})
        await self.load_rules(rule_ids)
        self.data.add_rule_matches(matches)

        res_medias = await self.load_medias_from_tweets()
        return res_medias


    '''
    Load from Tweets functions
    Used to expand data around a set of tweets
    '''

    async def load_medias_from_tweets(self, tweets: List[LinkedTweet] = None):
        if not tweets:
            tweets = self.data.get_linked_tweets(list(self.data.tweets.keys()))
        media_keys = sum([t.tweet.get_media_keys() for t in tweets], [])

        medias = await self.load_medias(media_keys)
        return medias

    async def load_polls_from_tweets(self, tweets: List[LinkedTweet]):
        if not tweets:
            tweets = self.data.get_linked_tweets(list(self.data.tweets.keys()))
        poll_ids = sum([(t.tweet.get_poll_ids()) for t in tweets], [])

        polls = await self.load_polls(poll_ids)
        return polls

    async def load_author_from_tweets(self, tweets: List[LinkedTweet]):
        if not tweets:
            tweets = self.data.get_linked_tweets(list(self.data.tweets.keys()))
        user_ids = [t.tweet.author_id for t in tweets if t.tweet.author_id]

        users = await self.load_users(ids=user_ids)
        return users

    async def load_replied_from_tweets(self, tweets: List[LinkedTweet]):
        if not tweets:
            tweets = self.data.get_linked_tweets(list(self.data.tweets.keys()))
        user_ids = [t.tweet.in_reply_to_user_id for t in tweets if t.tweet.in_reply_to_user_id]

        users = await self.load_users(ids=user_ids)
        return users

    async def load_users_from_tweets(self, tweets: List[LinkedTweet]):
        if not tweets:
            tweets = self.data.get_linked_tweets(list(self.data.tweets.keys()))

        res = await asyncio.gather(
            self.load_replied_from_tweets(tweets),
            self.load_author_from_tweets(tweets)
        )
        loaded = sum(res, [])
        return loaded

    async def load_rules_from_tweets(self, tweets: List[LinkedTweet] = None):
        if not tweets:
            tweets = self.data.get_linked_tweets(list(self.data.tweets.keys()))

        rule_ids = sum([[m.rule_id for m in self.data.rule_matches[t.tweet.id].values()] for t in tweets], [])
        rule_ids = self.loaded.only_new_rules(rule_ids)

        rules = await self.load_rules(rule_ids)
        return rules

    async def load_replied_tweet_from_tweets(self, tweets: List[LinkedTweet]):
        return await self._load_tweet_from_tweets(tweets, id_fn=lambda t: t.tweet.get_replied_to_id())

    async def load_retweeted_tweet_from_tweets(self, tweets: List[LinkedTweet]):
        return await self._load_tweet_from_tweets(tweets, id_fn=lambda t: t.tweet.get_retweeted_id())

    async def load_quoted_tweet_from_tweets(self, tweets: List[LinkedTweet]):
        return await self._load_tweet_from_tweets(tweets, id_fn=lambda t: t.tweet.get_quoted_id())

    async def load_conversation_tweet_from_tweets(self, tweets: List[LinkedTweet]):
        return await self._load_tweet_from_tweets(tweets, id_fn=lambda t: t.tweet.conversation_id)

    async def load_referenced_tweets_from_tweets(self, tweets: List[LinkedTweet]):
        res = await asyncio.gather(
            self.load_retweeted_tweet_from_tweets(tweets),
            self.load_replied_tweet_from_tweets(tweets),
            self.load_quoted_tweet_from_tweets(tweets),
            self.load_conversation_tweet_from_tweets(tweets)
        )
        loaded = sum([r for r in res if r], [])
        return loaded

    async def _load_tweet_from_tweets(self, tweets: List[LinkedTweet], id_fn: Callable):
        if not tweets:
            tweets = self.data.get_linked_tweets(list(self.data.tweets.keys()))
        tweet_ids = list({id_fn(t) for t in tweets})
        tweet_ids = [t for t in tweet_ids if t]

        tweet_res = await self.load_tweets(tweet_ids)
        return tweet_res

    async def load_all_from_tweets(self, tweets: List[LinkedTweet] = None):
        if not tweets:
            tweets = self.data.get_linked_tweets(list(self.data.tweets.keys()))

        res = await asyncio.gather(
            self.load_referenced_tweets_from_tweets(tweets),
            self.load_users_from_tweets(tweets),
            self.load_medias_from_tweets(tweets),
            self.load_polls_from_tweets(tweets)
        )
        return res
