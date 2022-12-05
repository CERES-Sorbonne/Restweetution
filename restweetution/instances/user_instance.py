import asyncio
from typing import Dict, List

from restweetution.collectors import Streamer
from restweetution.collectors.searcher import Searcher
from restweetution.models.config.user_config import RuleOptions, UserConfig, RuleConfig
from restweetution.storages.postgres_storage.postgres_storage import PostgresStorage


class UserInstance:
    _streamer: Streamer = None
    _searcher: Searcher = None

    searcher_task: asyncio.Task = None

    rule_options: Dict[int, RuleOptions] = {}

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
        searcher_rule = self._searcher.get_rule()
        self.user_config.searcher_task_config.rule = searcher_rule.config() if searcher_rule else None

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
            streamer_rules = await self._streamer.set_rules(task.rules)

            options = {r.query: r.options for r in task.rules}
            for rule in streamer_rules:
                self.rule_options[rule.id] = options[rule.query]

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
        self.rule_options = {
            r.id: self.rule_options[r.id] if r.id in self.rule_options else RuleOptions() for r in server_rules
        }

    async def streamer_add_rules(self, rules: List[RuleConfig]):
        server_rules = await self._streamer.add_rules(rules)
        for rule in server_rules:
            if rule.id not in self.rule_options:
                self.rule_options[rule.id] = RuleOptions()

    async def streamer_del_rules(self, ids: List[int]):
        await self._streamer.remove_rules(ids)
        for id_ in ids:
            self.rule_options.pop(id_)

    def _create_searcher(self):
        if self._searcher:
            raise Exception('Searcher already exist')
        self._searcher = Searcher(storage=self.storage, bearer_token=self.user_config.bearer_token)

    async def _load_searcher_task(self):
        task = self.user_config.searcher_task_config
        if task.rule is None:
            return
        rule = await self._searcher.set_rule(task.rule)
        if rule:
            self.rule_options[rule.id] = task.rule.options
        else:
            raise Exception('Could not set rule to searcher')
        if task.is_running:
            self.searcher_start()

    async def searcher_set_rule(self, rule: RuleConfig):
        if self._searcher.get_rule():
            self.rule_options.pop(self._searcher.get_rule().id)

        rule = await self._searcher.set_rule(rule)
        if rule:
            self.rule_options[rule.id] = RuleOptions()
        return rule

    def searcher_get_rule(self):
        return self._searcher.get_rule()

    def searcher_del_rule(self):
        self._searcher.remove_rule()

    def searcher_start(self):
        self._searcher.start_collection(fields=self.user_config.searcher_task_config.fields)

    def searcher_stop(self):
        self._searcher.stop_collection()

    def searcher_is_running(self):
        return self._searcher.is_running()
