from abc import ABC
from collections import defaultdict
from typing import List, Dict

from restweetution.models.bulk_data import BulkData
from restweetution.models.storage.custom_data import CustomData
from restweetution.models.twitter import Media, RestTweet, StreamRule
from restweetution.storages.storage import Storage

minimum_fields = [
    'id',
    'text',
    'created_at',
    'author_id',
    # 'conversation_id',
    # 'in_reply_to_user_id',
    # 'referenced_tweets',
    'attachments',
    # 'geo',
    # 'context_annotations',
    # 'entities',
    # 'withheld',
    # 'public_metrics',
    # 'organic_metrics',
    # 'promoted_metrics',
    # 'possibly_sensitive',
    # 'lang',
    # 'source',
    # 'reply_settings'
]


class DataUnit(dict):
    def __init__(self, id_: str, **kwargs):
        super().__init__(**kwargs)
        self['id'] = id_

    def id(self):
        return self['id']


class DataView(ABC):
    def __init__(self, name: str, in_storage: Storage, out_storage: Storage):
        self._view_name = name
        self.input = in_storage
        self.output = out_storage
        self._is_loaded = False
        self.datas: Dict[str, DataUnit] = {}

    async def load(self):
        pass

    async def save(self):
        to_save = []
        for d in self._get_datas():
            to_save.append(self._custom_data(d))
        await self.output.save_custom_datas(to_save)

    async def update(self, bulk_data: BulkData):
        pass

    def _custom_data(self, data: DataUnit):
        return CustomData(key=self._view_name, id=data['id'], data=data)

    def _get_datas(self) -> List[DataUnit]:
        return list(self.datas.values())

    def _add_datas(self, datas: List[DataUnit]):
        for d in datas:
            self.datas[d.id()] = d


class ElasticView(DataView):
    def __init__(self, in_storage, out_storage):
        super().__init__(name='elastic', in_storage=in_storage, out_storage=out_storage)
        self._cache = BulkData()
        self._media_to_tweets = defaultdict(list)

        in_storage.save_event.add(self.update)
        in_storage.update_event.add(self._update_sha1)

    async def load(self):
        await super().load()

        tweet_list = await self.input.get_tweets(fields=minimum_fields)
        tweet_list = [t for t in tweet_list if t.created_at]

        self._cache.add_tweets(tweet_list)
        self._cache_media_to_tweet(tweet_list)

        user_list = await self.input.get_users()
        self._cache.add_users(user_list)

        media_list = await self.input.get_medias()
        self._cache.add_medias(media_list)

        datas = self._compute_data(tweet_list)
        self._add_datas(datas)

    def _compute_data(self, tweet_list, tweet_to_rules=None):
        if tweet_to_rules is None:
            tweet_to_rules = defaultdict(set)

        res = []
        for tweet in tweet_list:
            has_media = len(tweet.attachments.media_keys) > 0
            is_retweet = None
            if tweet.referenced_tweets:
                for ref in tweet.referenced_tweets:
                    if ref.type == 'retweeted':
                        is_retweet = self._cache.users[self._cache.tweets[ref.id].author_id].username
            sha1 = []
            for media_key in tweet.attachments.media_keys:
                if media_key in self._cache.medias:
                    media = self._cache.medias[media_key]
                    if media.sha1:
                        sha1.append(media.sha1)

            data = DataUnit(id_=tweet.id,
                            text=tweet.text,
                            author=self._cache.users[tweet.author_id].username,
                            created_at=tweet.created_at,
                            has_media=has_media,
                            is_retweet=is_retweet,
                            rule_tags=list(tweet_to_rules[tweet.id]),
                            sha1=sha1)
            res.append(data)
        return res

    async def update(self, bulk_data: BulkData):
        tweets = [t for t in bulk_data.get_tweets() if t.id not in self._cache.tweets]
        self._cache += bulk_data

        self._cache_media_to_tweet(tweets)

        datas = self._compute_data(tweets, tweet_to_rules=self._compute_tweet_to_rules(bulk_data.get_rules()))
        self._add_datas(datas)

        await self._save_data_(datas)

    @staticmethod
    def _compute_tweet_to_rules(rules: List[StreamRule]):
        tweet_to_rules = defaultdict(set)
        for rule in rules:
            for tweet_id in rule.tweet_ids:
                tweet_to_rules[tweet_id].add(rule.tag)
        return tweet_to_rules

    async def _save_data_(self, datas: List[DataUnit]):
        to_save = [self._custom_data(d) for d in datas]
        await self.output.save_custom_datas(to_save)

    async def _update_sha1(self, medias: List[Media]):
        updated = []
        for media in medias:
            if media.sha1:
                tweets = self._media_to_tweets[media.media_key]
                for tweet in tweets:
                    data = self.datas[tweet.id]
                    if 'sha1' not in data:
                        data['sha1'] = [media.sha1]
                    else:
                        data['sha1'].append(media.sha1)
                    updated.append(data)
        await self._save_data_(updated)

    def _cache_media_to_tweet(self, tweets: List[RestTweet]):
        for tweet in tweets:
            if tweet.attachments.media_keys:
                for key in tweet.attachments.media_keys:
                    self._media_to_tweets[key].append(tweet)
