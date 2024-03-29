import asyncio
import logging
from datetime import datetime
from typing import List, Dict

from restweetution.collectors import Streamer
from restweetution.collectors.searcher import Searcher
from restweetution.instances.storage_instance import StorageInstance
from restweetution.models.bulk_data import BulkData
from restweetution.models.config.user_config import UserConfig, RuleConfig, CollectorConfig, CollectOptions
from restweetution.models.instance_update import InstanceUpdate
from restweetution.models.linked.linked_bulk_data import LinkedBulkData
from restweetution.models.storage.downloaded_media import DownloadedMedia
from restweetution.utils import AsyncEvent, fire_and_forget

logger = logging.getLogger('UserInterface')


class UserInstance:
    _streamer: Streamer = None
    _searcher: Searcher = None

    event = AsyncEvent()

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
        equal = await self._streamer.verify_config_equal_api_rules(config.rules)
        await self._streamer.sync_rules_from_api()

        if self._streamer.get_rules() and config.is_running and equal:
            self.streamer_start()

    async def streamer_sync(self):
        await self._streamer.sync_rules_from_api()

    async def streamer_verify(self):
        return await self._streamer.verify_api_sync()

    def streamer_has_conflict(self):
        return self._streamer.has_conflict()

    def _on_collect(self, collect_config: CollectorConfig):
        async def on_collect_event(bulk_data: BulkData):
            collect_options = collect_config.collect_options
            media_downloader = self.storage_instance.media_downloader
            elastic_dashboard = self.storage_instance.elastic_dashboard

            if collect_options.download_media():
                if not media_downloader:
                    logger.warning('No MediaDownloader set, tried to download media')
                else:
                    medias = bulk_data.get_medias()
                    media_to_tweet = bulk_data.compute_media_to_tweets()
                    callback = self._on_download_media(collect_config, bulk_data, media_to_tweet)

                    photos = [m for m in medias if m.type == 'photo']
                    videos = [m for m in medias if m.type == 'video']
                    gif = [m for m in medias if m.type == 'animated_gif']

                    if collect_options.download_photo:
                        media_downloader.download_medias(medias=photos, callback=callback)
                    if collect_options.download_video:
                        media_downloader.download_medias(medias=videos, callback=callback)
                    if collect_options.download_gif:
                        media_downloader.download_medias(medias=gif, callback=callback)

            if collect_options.elastic_dashboard and collect_options.elastic_dashboard_name:
                if not elastic_dashboard:
                    logger.warning('No elastic dashboard: Tried to send data to elastic dashboard')
                else:
                    linked = LinkedBulkData()
                    linked += bulk_data
                    elastic_dashboard.export(collect_options.elastic_dashboard_name, linked.get_linked_tweets())

        return on_collect_event

    def _on_download_media(self, collect_config: CollectorConfig, bulk_data: BulkData, media_to_tweet: Dict[str, set]):
        async def on_download_event(d_media: DownloadedMedia):
            collect_tasks = collect_config.collect_options
            elastic_dashboard = self.storage_instance.elastic_dashboard

            if collect_tasks.elastic_dashboard and collect_tasks.elastic_dashboard_name:
                if not elastic_dashboard:
                    logger.warning('No elastic dashboard: Tried to send data to elastic dashboard')
                bulk_data.add_downloaded_medias([d_media])
                only_ids = media_to_tweet[d_media.media_key]
                linked = LinkedBulkData()
                linked += bulk_data
                elastic_dashboard.export(collect_tasks.elastic_dashboard_name, linked.get_linked_tweets(list(only_ids)))

        return on_download_event

    def streamer_set_collect_options(self, options: CollectOptions):
        self.user_config.streamer_state.collect_options = options

    def streamer_get_collect_options(self):
        return self.user_config.streamer_state.collect_options

    def searcher_set_collect_options(self, options: CollectOptions):
        self.user_config.searcher_state.collect_options = options

    def searcher_get_collect_options(self):
        return self.user_config.searcher_state.collect_options

    def streamer_start(self):
        self._streamer.start_collection()

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
        # if config.fields:
        #     self._searcher.set_fields(config.fields)
        if config.time_window:
            self._searcher.load_time_window(config.time_window)

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

    def searcher_is_sleeping(self):
        return self._searcher.is_sleeping()

    def searcher_set_time_window(self, start: datetime = None, end: datetime = None, recent=True):
        self._searcher.set_time_window(start, end, recent)

    async def searcher_count(self, query: str, start: datetime = None, end: datetime = None, recent=True,
                             step: str = None):
        return await self._searcher.count(query=query, start=start, end=end, recent=recent, step=step)

    async def _searcher_update(self):
        self.write_config()
        update = InstanceUpdate(source='searcher', user_id=self.user_config.name)
        fire_and_forget(self.event(update))
        await self.storage_instance.storage.update_restweet_user([self.user_config])

    async def _streamer_update(self):
        self.write_config()
        update = InstanceUpdate(source='streamer', user_id=self.user_config.name)
        fire_and_forget(self.event(update))

    async def save_user_config(self):
        self.write_config()
        await self.storage_instance.storage.update_restweet_user([self.user_config])

    def searcher_get_fields(self):
        return self._searcher.get_fields()

    def searcher_get_time_window(self):
        return self._searcher.get_time_window()
