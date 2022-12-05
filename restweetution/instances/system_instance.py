from typing import Dict, List

from restweetution.instances.user_instance import UserInstance
from restweetution.models.config.system_config import SystemConfig
from restweetution.models.config.user_config import UserConfig
from restweetution.storages.postgres_storage.postgres_storage import PostgresStorage


class SystemInstance:
    system_config: SystemConfig
    storage: PostgresStorage
    user_instances: Dict[str, UserInstance] = {}

    def __init__(self, system_config: SystemConfig):
        self.system_config = system_config
        self.storage = PostgresStorage(**system_config.storage)

    async def save_user_config(self, user_id):
        user = self.user_instances[user_id]
        config = user.write_config()
        await self.storage.save_user_configs([config])

    async def add_user_instance(self, user_config: UserConfig):
        if user_config.bearer_token in self.user_instances:
            raise Exception('UserInstance with same bearer_token is already used ', user_config.bearer_token)

        user_instance = UserInstance(user_config, self.storage)
        await user_instance.start()
        self.user_instances[user_instance.get_name()] = user_instance
        return user_instance

    async def remove_user_instances(self, names: List[str]):
        for name in names:
            if name not in self.user_instances:
                raise Exception(f'No UserInstance with name [{name}] found | existing: [{self.user_instances.keys()}]')

        for name in names:
            self.user_instances.pop(name)
        await self.storage.del_user_configs(names)

    async def load_user_configs(self):
        user_configs = await self.storage.get_user_configs()
        for config in user_configs:
            await self.add_user_instance(config)

    def get_user_list(self):
        return list(self.user_instances.values())

    async def get_all_rules(self):
        return await self.storage.get_rules(fields=['id', 'tag', 'query', 'created_at'])

    async def get_all_rule_info(self):
        rules = await self.get_all_rules()
        count = await self.storage.get_rules_tweet_count()

        res = []
        for rule in rules:
            info = rule.dict()
            if rule.id in count:
                info['tweet_count'] = count[rule.id]
            else:
                info['tweet_count'] = 0
            res.append(info)
        return res