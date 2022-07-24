from abc import ABC
from typing import List, Dict

from restweetution.models.storage.bulk_data import BulkData
from restweetution.models.storage.custom_data import CustomData
from restweetution.models.storage.twitter import User
from restweetution.storage.storages.storage import Storage


class DataUnit(dict):
    def __init__(self, id_: str, **kwargs):
        super().__init__(**kwargs)
        self['id'] = id_


class DataView(ABC):
    def __init__(self, name: str, in_storage: Storage, out_storage: Storage):
        self._view_name = name
        self.input = in_storage
        self.output = out_storage
        self._is_loaded = False
        self._not_saved_ids = []
        self.data: List[DataUnit] = []

    async def load(self):
        self.data = []

    async def save(self):
        to_save = []
        for d in self.data:
            to_save.append(CustomData(key=self._view_name, id=d['id'], data=d))
        await self.output.save_custom_datas(to_save)

    async def update(self, bulk_data: BulkData):
        pass


class ElasticView(DataView):
    def __init__(self, in_storage, out_storage):
        super().__init__(name='elastic', in_storage=in_storage, out_storage=out_storage)

    async def load(self):
        await super().load()

        tweet_list = await self.input.get_tweets()
        tweet_by_id = {k: v for (k, v) in [(x.id, x) for x in tweet_list]}

        user_list = await self.input.get_users()
        user_by_id: Dict[str, User] = {k: v for (k, v) in [(x.id, x) for x in user_list]}

        for tweet in tweet_list:
            has_media = len(tweet.attachments.media_keys) > 0
            data = DataUnit(id_=tweet.id,
                            text=tweet.text,
                            author=user_by_id[tweet.author_id].name,
                            created_at=tweet.created_at,
                            has_media=has_media)
            self.data.append(data)
