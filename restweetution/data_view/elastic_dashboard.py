from collections import defaultdict
from typing import List, Set, Dict

from restweetution.data_view.data_view import DataView, DataUnit
from restweetution.models.bulk_data import BulkData
from restweetution.models.event_data import EventData
from restweetution.models.rule import Rule
from restweetution.models.storage.custom_data import CustomData
from restweetution.models.twitter import Tweet

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


class ElasticDashboard(DataView):
    def __init__(self, in_storage, out_storage, dashboard_name='elastic'):
        super().__init__(name=dashboard_name, in_storage=in_storage, out_storage=out_storage)
        self._media_to_tweet_ids = defaultdict(list)

        in_storage.save_event.add(self.add)
        in_storage.update_event.add(self._update_sha1)
        self.datas: Dict[str, DataUnit] = {}

    async def load(self):
        await super().load()
        bulk_data = BulkData()

        tweet_list = await self.input.get_tweets(fields=minimum_fields)
        tweet_list = [t for t in tweet_list if t.created_at]

        bulk_data.add_tweets(tweet_list)
        self._cache_media_to_tweet(tweet_list)

        user_list = await self.input.get_users()
        bulk_data.add_users(user_list)

        media_list = await self.input.get_medias()
        bulk_data.add_medias(media_list)

        rule_list = await self.input.get_rules()
        bulk_data.add_rules(rule_list)

        datas = self._compute_data(bulk_data)
        self._add_datas(datas)

    @staticmethod
    def _compute_data(bulk_data: BulkData, tweet_ids: Set[str] = None):
        tweet_to_rules = ElasticDashboard._compute_tweet_to_rules(bulk_data.get_rules())

        tweet_list = bulk_data.get_tweets()
        if tweet_ids:
            tweet_list = [t for t in tweet_list if t.id in tweet_ids]

        res = []
        for tweet in tweet_list:
            has_media = len(tweet.attachments.media_keys) > 0
            is_retweet = None
            if tweet.referenced_tweets:
                for ref in tweet.referenced_tweets:
                    if ref.type == 'retweeted':
                        is_retweet = bulk_data.users[bulk_data.tweets[ref.id].author_id].username
            sha1 = []
            for media_key in tweet.attachments.media_keys:
                if media_key in bulk_data.medias:
                    media = bulk_data.medias[media_key]
                    if media.sha1:
                        sha1.append(media.sha1)

            data = DataUnit(id_=tweet.id,
                            text=tweet.text,
                            author=bulk_data.users[tweet.author_id].username,
                            created_at=tweet.created_at,
                            has_media=has_media,
                            is_retweet=is_retweet,
                            rule_tags=list(tweet_to_rules[tweet.id]),
                            sha1=sha1)
            res.append(data)
        return res

    async def add(self, event_data: EventData):

        bulk_data = event_data.data
        self._cache_media_to_tweet(bulk_data.get_tweets())

        datas = self._compute_data(bulk_data, event_data.added.tweets)
        self._add_datas(datas)

        await self._save_data_(datas)

    @staticmethod
    def _compute_tweet_to_rules(rules: List[Rule]):
        tweet_to_rules = defaultdict(set)
        for rule in rules:
            for tweet_id in rule.tweet_ids:
                tweet_to_rules[tweet_id].add(rule.tag)
        return tweet_to_rules

    async def _save_data_(self, datas: List[DataUnit]):
        to_save = [self._custom_data(d) for d in datas]
        await self.output.save_custom_datas(to_save)

    async def _update_sha1(self, event_data: EventData):
        if not event_data.updated.medias:
            return
        medias = [m for m in event_data.data.get_medias() if m.media_key in event_data.updated.medias]
        updated = []
        for media in medias:
            if media.sha1:
                tweet_ids = self._media_to_tweet_ids[media.media_key]
                for tweet_id in tweet_ids:
                    data = self.datas[tweet_id]
                    if 'sha1' not in data:
                        data['sha1'] = [media.sha1]
                    else:
                        data['sha1'].append(media.sha1)
                    updated.append(data)
        await self._save_data_(updated)

    def _cache_media_to_tweet(self, tweets: List[Tweet]):
        for tweet in tweets:
            if tweet.attachments.media_keys:
                for key in tweet.attachments.media_keys:
                    self._media_to_tweet_ids[key].append(tweet.id)

    def _custom_data(self, data: DataUnit):
        return CustomData(key=self._view_name, id=data['id'], data=data)

    def _get_datas(self) -> List[DataUnit]:
        return list(self.datas.values())

    def _add_datas(self, datas: List[DataUnit]):
        for d in datas:
            self.datas[d.id()] = d

    async def save(self, **kwargs):
        to_save = []
        for d in self._get_datas():
            to_save.append(self._custom_data(d))
        await self.output.save_custom_datas(to_save)
