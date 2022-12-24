import asyncio
from collections import defaultdict
from typing import List, Dict

from restweetution.models.bulk_data import BulkData
from restweetution.models.storage.downloaded_media import DownloadedMedia
from restweetution.models.storage.custom_data import CustomData
from restweetution.storages.exporter.exporter import Exporter

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


class Dashboard:
    def __init__(self, exporter: Exporter):
        self.exporter = exporter

    @staticmethod
    def compute(bulk_data: BulkData, key: str, only_ids: List[str] = None):
        res = []
        tweet_tags = defaultdict(set)
        for rule in bulk_data.get_rules():
            for collected in rule.collected_tweets_list():
                tweet_tags[collected.tweet_id].update(bulk_data.rules[collected.rule_id].tag.split(','))

        if only_ids:
            tweet_list = [t for t in bulk_data.get_tweets() if t.id in only_ids]
        else:
            tweet_list = bulk_data.get_tweets()

        for tweet in tweet_list:
            custom_data = CustomData(key=key, id=tweet.id)
            data = custom_data.data

            data['id'] = tweet.id
            data['text'] = tweet.text

            if tweet.author_id and bulk_data.users[tweet.author_id]:
                data['author'] = bulk_data.users[tweet.author_id].username
            if tweet.created_at:
                data['created_at'] = tweet.created_at
            if tweet.attachments and tweet.attachments.media_keys:
                data['has_media'] = True
            retweet_id = tweet.retweet_id()
            if retweet_id:
                data['retweet_id'] = retweet_id
                retweeted = bulk_data.tweets[retweet_id]
                if retweeted and retweeted.author_id:
                    data['retweet_author_id'] = retweeted.author_id
                    if bulk_data.users[retweeted.author_id]:
                        data['retweet_author_username'] = bulk_data.users[retweeted.author_id].username
            if tweet_tags[tweet.id]:
                data['rule_tags'] = ','.join(list(tweet_tags[tweet.id]))

            res.append(custom_data)
        return res

    def compute_and_save(self, bulk_data: BulkData, key: str):
        res = self.compute(bulk_data, key)
        asyncio.create_task(self.exporter.save_custom_datas(res))

    def update_sha1_and_save(self, bulk_data: BulkData, d_medias: List[DownloadedMedia], key: str):
        media_key_to_d_media: Dict[str, DownloadedMedia] = {d.media_key: d for d in d_medias}
        media_key_to_tweet_id = defaultdict(set)
        tweet_id_to_media_key = defaultdict(set)
        for tweet in bulk_data.get_tweets():
            if tweet.attachments and tweet.attachments.media_keys:
                for media_key in tweet.attachments.media_keys:
                    if media_key in list(media_key_to_d_media.keys()):
                        media_key_to_tweet_id[media_key].add(tweet.id)
                        tweet_id_to_media_key[tweet.id].add(media_key)
        res = self.compute(bulk_data, key, only_ids=list(tweet_id_to_media_key.keys()))
        for r in res:
            media_keys = list(tweet_id_to_media_key[r.id])
            sha1s = [media_key_to_d_media[m].sha1 for m in media_keys]
            image_names = [media_key_to_d_media[m].sha1 + '.' + media_key_to_d_media[m].format for m in media_keys]

            r.data['sha1'] = sha1s
            r.data['image_name'] = image_names

        asyncio.create_task(self.exporter.save_custom_datas(res))



