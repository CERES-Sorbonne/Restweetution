import json
import os

import yaml

from restweetution.collectors import AsyncStreamer
from restweetution.collectors.async_client import AsyncClient
from restweetution.models.config.main_config import MainConfig
from restweetution.models.stream_config import StreamConfig
from restweetution.storage.async_storage_manager import AsyncStorageManager
from restweetution.storage.elastic_storage.elastic_storage import ElasticTweetStorage


def get_config_from_file(file_path: str):
    conf = read_conf(path_to_config_file=file_path)
    return build_config(conf)


def read_conf(path_to_config_file: str):
    if path_to_config_file.split('.')[-1] == 'json':
        try:
            with open(path_to_config_file, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON provided, the following error occurred trying to open the config: {e}")

    elif path_to_config_file.split('.')[-1] == 'yaml':
        try:
            with open(path_to_config_file, 'r') as f:
                return yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML provided, the following error occurred trying to open the config: {e}")
    else:
        raise ValueError("Invalid config provided")


def build_config(data: dict):
    main_conf = MainConfig()

    parse_client_config(main_conf, data)
    parse_storage_config(main_conf, data)
    parse_streamer_config(main_conf, data)

    return main_conf


def parse_streamer_config(main_conf: MainConfig, data: dict):
    if main_conf.client and main_conf.storage_manager:
        streamer = AsyncStreamer(client=main_conf.client, storage_manager=main_conf.storage_manager)
        if 'streamer' in data:
            s_data = data['streamer']
            if 'verbose' in s_data:
                streamer.set_verbose(s_data['verbose'])
            if 'rules' in s_data:
                streamer.preset_stream_rules(s_data['rules'])
        main_conf.streamer = streamer


def parse_client_config(main_conf: MainConfig, data: dict):
    if 'client' not in data:
        return
    main_conf.client = AsyncClient(token=data['client']['token'])


def parse_storage_config(main_conf: MainConfig, data: dict):
    if 'tweet_storages' in data:
        for key, value in data['tweet_storages'].items():
            main_conf.tweet_storages.append(create_storage(key, value))
    if 'storage_tags' in data:
        main_conf.storage_tags = data['storage_tags']
        for storage in main_conf.tweet_storages:
            if storage.name not in main_conf.storage_tags:
                main_conf.storage_tags[storage.name] = []
    main_conf.storage_manager = create_storage_manager(main_conf)


def create_storage_manager(main_conf: MainConfig) -> AsyncStorageManager:
    manager = AsyncStorageManager()
    for storage in main_conf.tweet_storages:
        manager.add_storage(storage=storage, tags=main_conf.storage_tags[storage.name])
    return manager


def create_storage(name: str, data: dict):
    if data['type'] == 'elastic':
        return ElasticTweetStorage(name=name,
                                   es_url=data['url'],
                                   es_user=data['user'],
                                   es_pwd=data['pwd'])
