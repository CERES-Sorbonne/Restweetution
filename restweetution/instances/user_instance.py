import asyncio
from datetime import datetime
from typing import List

from restweetution.collectors import Streamer
from restweetution.collectors.searcher import Searcher
from restweetution.models.config.user_config import UserConfig, RuleConfig
from restweetution.models.searcher import SearcherConfig
from restweetution.storages.postgres_storage.postgres_storage import PostgresStorage


class UserInstance:
    _streamer: Streamer = None
    _searcher: Searcher = None

    searcher_task: asyncio.Task = None

    def __init__(self, user_config: UserConfig, storage: PostgresStorage):
        self.user_config = user_config
        self.storage = storage

        self._create_streamer()
        self._create_searcher()

    async def start(self):
        await self._load_streamer_task()
        await self._load_searcher_task()

    def write_config(self):
        self.user_config.streamer_task_config.is_running = self.streamer_is_running()
        self.user_config.streamer_task_config.rules = [r.config() for r in self._streamer.get_rules()]

        self.user_config.searcher_task_config.is_running = self.searcher_is_running()
        self.user_config.searcher_task_config.config = self._searcher.get_config()

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
        self._streamer = Streamer(bearer_token=self.user_config.bearer_token, storage=self.storage)

    async def _load_streamer_task(self):
        task = self.user_config.streamer_task_config
        if task.rules:
            await self._streamer.set_rules(task.rules)

        if self._streamer.get_rules() and task.is_running:
            self.streamer_start()

    def streamer_start(self):
        self._streamer.start_collection(fields=self.user_config.streamer_task_config.fields)

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

    def _create_searcher(self):
        if self._searcher:
            raise Exception('Searcher already exist')
        self._searcher = Searcher(storage=self.storage, bearer_token=self.user_config.bearer_token)
        self._searcher.event_update.add(self.save_searcher_config)

    async def _load_searcher_task(self):
        task = self.user_config.searcher_task_config
        if task.config.rule is None:
            return

        await self._searcher.set_config(task.config)

        if task.is_running:
            self.searcher_start()

    async def searcher_set_rule(self, rule: RuleConfig):
        rule = await self._searcher.set_rule(rule)
        await self.save_searcher_config(self._searcher.get_config())
        return rule

    def searcher_get_rule(self):
        return self._searcher.get_rule()

    def searcher_del_rule(self):
        self._searcher.remove_rule()

    def searcher_start(self):
        self._searcher.start_collection()

    def searcher_stop(self):
        self._searcher.stop_collection()

    def searcher_is_running(self):
        return self._searcher.is_running()

    def searcher_set_time_window(self, start: datetime = None, end: datetime = None):
        self._searcher.set_time_window(start=start, end=end)

    def searcher_get_config(self):
        return self._searcher.get_config()

    async def save_searcher_config(self, config: SearcherConfig):
        self.user_config.searcher_task_config.config = config
        # self.write_config()
        await self.storage.save_user_configs([self.user_config])
