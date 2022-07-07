import json

import yaml

from restweetution.collectors import Streamer
from restweetution.twitter_client import TwitterClient
from restweetution.models.config.main_config import MainConfig
from restweetution.models.config.query_params_config import ALL_CONFIG, MEDIUM_CONFIG, BASIC_CONFIG
from restweetution.models.tweet_config import QueryParams
from restweetution.storage.storage_manager import StorageManager
from restweetution.storage.elastic_storage.elastic_storage import ElasticTweetStorage
from restweetution.storage.postgres_storage.postgres_storage import PostgresStorage


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

    parse_client_config(main_conf, data)
    parse_storage_config(main_conf, data)
    parse_streamer_config(main_conf, data)

    return main_conf


def parse_streamer_config(main_conf: MainConfig, data: dict):
    """
    Parsing of streamer options
    :param main_conf: MainConfig
    :param data: raw config data
    """
    if main_conf.client and main_conf.storage_manager:
        streamer = Streamer(client=main_conf.client, storage_manager=main_conf.storage_manager)
        if 'streamer' in data:
            s_data = data['streamer']
            if 'verbose' in s_data:
                main_conf.streamer_verbose = s_data['verbose']
                streamer.set_verbose(main_conf.streamer_verbose)
            if 'rules' in s_data:
                main_conf.streamer_rules = s_data['rules']
                streamer.pre_set_stream_rules(main_conf.streamer_rules)
            if 'query_params' in s_data:
                parse_query_params(main_conf, s_data['query_params'])
                streamer.set_query_params(main_conf.streamer_query_params)
        main_conf.streamer = streamer


def parse_query_params(main_conf: MainConfig, data: dict):
    """
    Parse query params from config
    :param main_conf: MainConfig to populate
    :param data: query_params data from config
    """
    params = data
    if 'pre_set' in data:
        value = data['pre_set'].lower()
        if value == 'all':
            params = ALL_CONFIG
        elif value == 'medium':
            params = MEDIUM_CONFIG
        elif value == 'basic':
            params = BASIC_CONFIG
    elif 'file' in data:
        params = QueryParams(**read_conf(data['file']))

    main_conf.streamer_query_params = params


def parse_client_config(main_conf: MainConfig, data: dict):
    """
    Parsing of client options
    :param main_conf: MainConfig
    :param data: raw config data
    """
    if 'client' not in data:
        return
    main_conf.client = TwitterClient(token=data['client']['token'])


def parse_storage_config(main_conf: MainConfig, data: dict):
    """
    Parsing of storage options
    :param main_conf: MainConfig
    :param data: raw config data
    """
    if 'tweet_storages' in data:
        for key, value in data['tweet_storages'].items():
            main_conf.storage_tweet_storages.append(create_storage(key, value))
    if 'storage_tags' in data:
        main_conf.storage_tags = data['storage_tags']
        for storage in main_conf.storage_tweet_storages:
            if storage.name not in main_conf.storage_tags:
                main_conf.storage_tags[storage.name] = []
    main_conf.storage_manager = create_storage_manager(main_conf)


def create_storage_manager(main_conf: MainConfig) -> StorageManager:
    """
    Create a storage_manager and set parameters according to config
    :param main_conf: MainConfig
    :return: storage_manager
    """
    manager = StorageManager()
    for storage in main_conf.storage_tweet_storages:
        if not main_conf.storage_tags or not main_conf.storage_tags[storage.name]:
            tags = []
        else:
            tags = main_conf.storage_tags[storage.name]

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
        return ElasticTweetStorage(name=name, **data)
    if storage_type == 'postgres':
        return PostgresStorage(name=name, **data)
