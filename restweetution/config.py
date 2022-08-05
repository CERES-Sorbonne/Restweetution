import json
from typing import Optional

import yaml

from restweetution.collectors import Streamer
from restweetution.models.config.main_config import MainConfig
from restweetution.models.config.stream_query_params import ALL_CONFIG, MEDIUM_CONFIG, BASIC_CONFIG
from restweetution.models.config.tweet_config import QueryFields
from restweetution.models.rule import StreamerRule
from restweetution.storage_manager import StorageManager
from restweetution.storages.elastic_storage.elastic_storage import ElasticStorage
from restweetution.storages.postgres_storage.postgres_storage import PostgresStorage


def get_config_from_file(file_path: str):
    """
    Builds a config from the given file_path
    :param file_path: path of the config file
    :return: MainConfig object
    """
    conf = read_conf(file_path=file_path)
    return build_config(conf)


def read_conf(file_path: str):
    """
    Read config file. Supports json and yaml
    :param file_path: path to config file
    :return: parsed value as Dict
    """
    if not file_path:
        raise ValueError('Config file path is empty ! You can set the path with CONFIG=<path>')
    if file_path.split('.')[-1] == 'json':
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON provided, the following error occurred trying to open the config: {e}")

    elif file_path.split('.')[-1] == 'yaml':
        try:
            with open(file_path, 'r') as f:
                return yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML provided, the following error occurred trying to open the config: {e}")
    else:
        raise ValueError("Invalid config provided")


def build_config(data: dict):
    """
    Builds the MainConfig with the config data
    The function instantiate usable objects
    :param data: dict containing the raw config data
    :return: the final MainConfig object
    """
    main_conf = MainConfig()

    parse_auth_config(main_conf, data)
    parse_storage_config(main_conf, data)
    parse_storage_manager_config(main_conf, data)
    parse_streamer_config(main_conf, data)
    parse_query_fields(main_conf, data)

    return main_conf


def parse_streamer_config(main_conf: MainConfig, data: dict):
    """
    Parsing of streamer options
    :param main_conf: MainConfig
    :param data: raw config data
    """
    if main_conf.storage_manager:
        streamer = Streamer(bearer_token=main_conf.bearer_token, storage_manager=main_conf.storage_manager)
        if 'streamer' in data:
            s_data = data['streamer']
            if 'verbose' in s_data:
                main_conf.streamer_verbose = s_data['verbose']
                # streamer.set_verbose(main_conf.streamer_verbose)
            if 'rules' in s_data:
                main_conf.streamer_rules = [StreamerRule(**r) for r in s_data['rules']]
        main_conf.streamer = streamer


def parse_query_fields(main_conf: MainConfig, data: dict):
    """
    Parse query params from config
    :param main_conf: MainConfig to populate
    :param data: query_params data from config
    """
    if 'query_fields' in data:
        data = data['query_fields']
        fields = data
        if 'preset' in data:
            value = data['preset'].lower()
            if value == 'all':
                fields = ALL_CONFIG
            elif value == 'medium':
                fields = MEDIUM_CONFIG
            elif value == 'basic':
                fields = BASIC_CONFIG
        elif 'file' in data:
            fields = QueryFields(**read_conf(data['file']))

        main_conf.query_fields = fields


def parse_auth_config(main_conf: MainConfig, data: dict):
    """
    Parsing of client options
    :param main_conf: MainConfig
    :param data: raw config data
    """
    if 'bearer_token' in data:
        main_conf.bearer_token = data['bearer_token']


def parse_storage_config(main_conf: MainConfig, data: dict):
    """
    Parsing of storage options
    :param main_conf: MainConfig
    :param data: raw config data
    """
    if 'storages' in data:
        for key, value in data['storages'].items():
            storage = create_storage(key, value)
            main_conf.storage_list.append(storage)
            main_conf.storages[storage.name] = storage


def parse_storage_manager_config(main_conf: MainConfig, data: dict):
    if 'storage_manager' not in data:
        return
    data = data['storage_manager']
    if data is None:
        return

    if 'main_storage' not in data:
        return

    main_storage_name = data['main_storage']

    storage_tags = {main_storage_name: []}  # default value
    if 'tags' in data and data['tags']:
        for s_name in data['tags']:
            tags = data['tags'][s_name]
            if tags is True:
                tags = []
            storage_tags[s_name] = tags

    if 'media_download' in data:
        main_conf.media_download = data['media_download']
    if 'media_root_dir' in data:
        main_conf.media_root_dir = data['media_root_dir']

    main_conf.storage_tags = storage_tags
    main_conf.storage_manager = create_storage_manager(main_conf, main_storage_name)


def create_storage_manager(main_conf: MainConfig, main_storage_name: str) -> Optional[StorageManager]:
    """
    Create a storage_manager and set parameters according to config
    :param main_conf: MainConfig
    :param main_storage_name: name of the main storage
    :return: storage_manager
    """
    main_storage = main_conf.storages[main_storage_name]

    manager = StorageManager(main_storage=main_storage,
                             main_tags=main_conf.storage_tags[main_storage.name],
                             media_root_dir=main_conf.media_root_dir,
                             download_media=main_conf.media_download)
    for s_name in main_conf.storage_tags:
        if s_name == main_storage_name:
            continue
        storage = main_conf.storages[s_name]
        tags = main_conf.storage_tags[s_name]
        manager.add_storage(storage=storage, tags=tags)
    return manager


def create_storage(name: str, data: dict):
    """
    Create a storage and set parameters according to config
    :param name: name of the storage, used for identification
    :param data: raw config data
    :return: storage
    """
    storage_type = data['type']
    if storage_type == 'elastic':
        return ElasticStorage(name=name, **data)
    if storage_type == 'postgres':
        return PostgresStorage(name=name, **data)
