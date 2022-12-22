import asyncio
import logging
from typing import List

from restweetution.collectors import Streamer
from restweetution.collectors.searcher import Searcher
from restweetution.instances.storage_instance import StorageInstance
from restweetution.models.bulk_data import BulkData
from restweetution.models.config.downloaded_media import DownloadedMedia
from restweetution.models.config.user_config import UserConfig, RuleConfig, CollectorConfig, CollectTasks
from restweetution.models.instance_update import InstanceUpdate
from restweetution.models.searcher import TimeWindow
from restweetution.utils import Event

logger = logging.getLogger('UserInterface')


class UserInstance:
    _streamer: Streamer = None
    _searcher: Searcher = None

    event = Event()

    def __init__(self, user_config: UserConfig, storage_instance: StorageInstance):
        self.user_config = user_config
        self.storage_instance = storage_instance

        self._create_streamer()
        self._create_searcher()

    async def start(self):
        await self._load_streamer()
        await self._load_searcher()

    def write_config(self):
        self.user_config.streamer_state.is_running = self.streamer_is_running()
        self.user_config.streamer_state.rules = [r.config() for r in self._streamer.get_rules()]

        self.user_config.searcher_state.is_running = self.searcher_is_running()
        self.user_config.searcher_state.time_window = self._searcher.get_time_window()
        self.user_config.searcher_state.fields = self._searcher.get_fields()

        searcher_rule = self._searcher.get_rule()
        if searcher_rule:
            self.user_config.searcher_state.rule = searcher_rule.config()
        else:
            self.user_config.searcher_state.rule = None

        return self.user_config

    def get_bearer_token(self):
        return self.user_config.bearer_token

    def get_name(self):
        return self.user_config.name

    async def test_rule(self, rule: RuleConfig):
        res = await self._streamer._client.test_rule(rule)
        return res

    def _create_streamer(self):
        if self._streamer:
            raise Exception('Streamer already exist')
        self._streamer = Streamer(bearer_token=self.user_config.bearer_token, storage=self.storage_instance.storage)
        self._streamer.event_update.add(self._streamer_update)
        self._streamer.event_collect.add(self._on_collect(self.user_config.streamer_state))

    async def _load_streamer(self):
        config = self.user_config.streamer_state
        if config.rules:
            await self._streamer.set_rules(config.rules)

        if self._streamer.get_rules() and config.is_running:
            self.streamer_start()

    def _on_collect(self, collect_config: CollectorConfig):
        async def on_collect_event(bulk_data: BulkData):
            collect_tasks = collect_config.collect_tasks
            media_downloader = self.storage_instance.media_downloader
            elastic_dashboard = self.storage_instance.elastic_dashboard

            if collect_tasks.download_media:
                if not media_downloader:
                    logger.warning('No MediaDownloader set, tried to download media')
                else:
                    # logger.info(f'collected medias: {len(bulk_data.get_medias())}')
                    media_downloader.download_medias(bulk_data.get_medias(), self._on_download_media(collect_config, bulk_data))
            if collect_tasks.elastic_dashboard and collect_tasks.elastic_dashboard_name:
                if not elastic_dashboard:
                    logger.warning('No elastic dashboard: Tried to send data to elastic dashboard')
                else:
                    elastic_dashboard.compute_and_save(bulk_data, collect_tasks.elastic_dashboard_name)

        return on_collect_event

    def _on_download_media(self, collect_config: CollectorConfig, bulk_data: BulkData):
        async def on_download_event(d_media: DownloadedMedia):
            collect_tasks = collect_config.collect_tasks
            elastic_dashboard = self.storage_instance.elastic_dashboard

            if collect_tasks.elastic_dashboard and collect_tasks.elastic_dashboard_name:
                if not elastic_dashboard:
                    logger.warning('No elastic dashboard: Tried to send data to elastic dashboard')
                elastic_dashboard.update_sha1_and_save(bulk_data, [d_media], collect_tasks.elastic_dashboard_name)
        return on_download_event

    def streamer_set_collect_tasks(self, tasks: CollectTasks):
        self.user_config.streamer_state.collect_tasks = tasks

    def streamer_get_collect_tasks(self):
        return self.user_config.streamer_state.collect_tasks

    def searcher_set_collect_tasks(self, tasks: CollectTasks):
        self.user_config.searcher_state.collect_tasks = tasks

    def searcher_get_collect_tasks(self):
        return self.user_config.searcher_state.collect_tasks

    def streamer_start(self):
        self._streamer.start_collection(fields=self.user_config.streamer_state.fields)

    def streamer_stop(self):
        self._streamer.stop_collection()

    def streamer_is_running(self):
        return self._streamer.is_running()

    def streamer_get_rules(self):
        return self._streamer.get_rules()

    async def streamer_get_api_rules(self):
        return await self._streamer.get_api_rules()

    async def streamer_set_rules(self, rules: List[RuleConfig]):
        server_rules = await self._streamer.set_rules(rules)
        return server_rules

    async def streamer_add_rules(self, rules: List[RuleConfig]):
        server_rules = await self._streamer.add_rules(rules)
        return server_rules

    async def streamer_del_rules(self, ids: List[int]):
        await self._streamer.remove_rules(ids)

    def streamer_get_count(self):
        return self._streamer.get_count()

    def _create_searcher(self):
        if self._searcher:
            raise Exception('Searcher already exist')
        self._searcher = Searcher(storage=self.storage_instance.storage, bearer_token=self.user_config.bearer_token)
        self._searcher.event_update.add(self._searcher_update)
        self._searcher.event_collect.add(self._on_collect(self.user_config.searcher_state))

    async def _load_searcher(self):
        config = self.user_config.searcher_state

        if config.rule:
            await self._searcher.set_rule(config.rule)
        if config.fields:
            self._searcher.set_fields(config.fields)
        if config.time_window:
            self._searcher.set_time_window(config.time_window, reset=False)

        if config.is_running and config.rule:
            try:
                await self.searcher_start()
            except Exception as e:
                logger.warning(e)
                config.is_running = False

    async def searcher_set_rule(self, rule: RuleConfig):
        rule = await self._searcher.set_rule(rule)
        await self.save_user_config()
        return rule

    def searcher_get_rule(self):
        return self._searcher.get_rule()

    def searcher_del_rule(self):
        self._searcher.remove_rule()

    async def searcher_start(self):
        await self._searcher.collect_count_test()
        self._searcher.start_collection()

    def searcher_stop(self):
        self._searcher.stop_collection()

    def searcher_is_running(self):
        return self._searcher.is_running()

    def searcher_set_time_window(self, time_window: TimeWindow):
        self._searcher.set_time_window(time_window)

    async def _searcher_update(self):
        self.write_config()
        update = InstanceUpdate(source='searcher', user_id=self.user_config.name)
        asyncio.create_task(self.event(update))
        await self.storage_instance.storage.update_restweet_user([self.user_config])

    async def _streamer_update(self):
        self.write_config()
        update = InstanceUpdate(source='streamer', user_id=self.user_config.name)
        asyncio.create_task(self.event(update))

    async def save_user_config(self):
        self.write_config()
        await self.storage_instance.storage.update_restweet_user([self.user_config])

    def searcher_get_fields(self):
        return self._searcher.get_fields()

    def searcher_get_time_window(self):
        return self._searcher.get_time_window()
