import asyncio
import logging
from typing import List

from restweetution.collectors import Streamer
from restweetution.models.config.config import Config
from restweetution.storage_manager import StorageManager

logger = logging.getLogger('Restweetution')


class Restweetution:
    def __init__(self, config):
        self._config: Config = config
        self._streamer: Streamer = config.streamer
        self._streamer_rules = config.streamer_rules
        self._searcher = config.searcher
        self._searcher_rule = config.searcher_rule
        self._storage_manager: StorageManager = config.storage_manager

        self._streamer_task = None

    async def init_streamer(self):
        self._streamer_rules = await self._streamer.set_rules(self._streamer_rules)

    def start_streamer(self):
        if self._streamer_task:
            logger.warning('Streamer is Already collecting')
            return

        self._streamer_task = asyncio.create_task(self._streamer.collect(fields=self._config.query_fields))

    def stop_streamer(self):
        if self._streamer_task:
            self._streamer_task.cancel()
            self._streamer_task = None

    def is_streamer_running(self):
        return self._streamer_task is not None

    def get_streamer_rules(self):
        return self._streamer.get_rules()

    async def add_streamer_rules(self, rules: List):
        self._streamer_rules = await self._streamer.add_rules(rules)

    async def remove_streamer_rules(self, ids):
        await self._streamer.remove_rules(ids)

    def is_media_downloader_active(self):
        return self._storage_manager.get_media_downloader().is_active()

    def is_media_downloader_downloading(self):
        return self._storage_manager.get_media_downloader().is_downloading()

    def set_media_downloader_active(self, value):
        return self._storage_manager.get_media_downloader().set_active(value)

    def get_media_downloader_queue_size(self):
        return self._storage_manager.get_media_downloader().get_queue_size()

    def get_media_root_dir(self):
        return self._storage_manager.get_media_downloader().get_root_dir()

    def get_actual_media_download(self):
        return self._storage_manager.get_media_downloader().actual_download
