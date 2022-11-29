import asyncio
import logging
from abc import ABC
from typing import List, Dict, Optional, Set

from restweetution.collectors import Streamer
from restweetution.collectors.searcher import Searcher
from restweetution.instances.user_instance import UserInstance
from restweetution.models.config.config import Config
from restweetution.models.config.system_config import SystemConfig
from restweetution.models.config.user_config import UserConfig, RuleOptions
from restweetution.models.rule import StreamerRule, SearcherRule
from restweetution.storages.postgres_storage.postgres_storage import PostgresStorage

logger = logging.getLogger('Restweetution')


class Restweetution:
    def __init__(self, system_config: SystemConfig):

        self.storage: PostgresStorage = config.storage
        #
        # self._all_rules_cache = []
        #
        # self._streamer_task = None

    async def start_streamer(self, user: UserInstance):
        if user.user_config.streamer_task_config:
            await user._streamer.add_rules(user.user_config.streamer_task_config.rules)

    async def init_streamer(self):
        await self._config.read_persistent_config()

        if self._config.streamer_rules:
            self._config.streamer_rules = await self._streamer.set_rules(self._config.streamer_rules)

    def start_streamer(self):
        if self._streamer_task:
            logger.warning('Streamer is Already collecting')
            return

        self._streamer_task = asyncio.create_task(self._streamer.collect(fields=self._config.query_fields))

    def stop_streamer(self):
        if self._streamer_task:
            self._streamer_task.cancel()
            self._streamer_task = None

    async def get_all_rules(self, type_: str = None):
        return await self.storage.get_rules(fields=['id', 'type', 'tag', 'query', 'created_at'], type_=type_)

    async def get_all_rule_info(self, type_: str = None):
        rules = await self.get_all_rules(type_=type_)
        count = await self.storage.main_storage.get_rules_tweet_count()

        res = []
        for rule in rules:
            info = rule.dict()
            if rule.id in count:
                info['tweet_count'] = count[rule.id]
            else:
                info['tweet_count'] = 0
            res.append(info)
        return res

    def is_streamer_running(self):
        return self._streamer_task is not None

    def get_active_streamer_rules(self):
        return self._streamer.get_rules()

    async def get_streamer_api_rules(self):
        return await self._streamer.get_api_rules()

    async def add_streamer_rules(self, rules: List):
        self._config.streamer_rules = await self._streamer.add_rules(rules)
        await self._config.write_config()

    async def remove_streamer_rules(self, ids):
        self._config.streamer_rules = await self._streamer.remove_rules(ids)
        await self._config.write_config()

    def is_media_downloader_active(self):
        return self.storage.get_media_downloader().is_active()

    def is_media_downloader_downloading(self):
        return self.storage.get_media_downloader().is_downloading()

    def set_media_downloader_active(self, value):
        return self.storage.get_media_downloader().set_active(value)

    def get_media_downloader_queue_size(self):
        return self.storage.get_media_downloader().get_queue_size()

    def get_media_root_dir(self):
        return self.storage.get_media_downloader().get_root_dir()

    def get_actual_media_download(self):
        return self.storage.get_media_downloader().actual_download
