import json

import yaml

from restweetution.collectors import Streamer
from restweetution.collectors.searcher import Searcher
from restweetution.media_downloader import MediaDownloader
from restweetution.models.config.config import Config
from restweetution.models.config.stream_query_params import ALL_CONFIG, MEDIUM_CONFIG, BASIC_CONFIG
from restweetution.models.config.system_config import SystemConfig
from restweetution.models.config.tweet_config import QueryFields
from restweetution.models.config.user_config import UserConfig
from restweetution.models.rule import StreamerRule, SearcherRule
from restweetution.storages.elastic_storage.elastic_storage import ElasticStorage
from restweetution.storages.exporter.csv_exporter import CSVExporter
from restweetution.storages.postgres_storage.postgres_storage import PostgresStorage


def get_config_from_file(file_path: str):
    """
    Builds a config from the given file_path
    :param file_path: path of the config file
    :return: Config object
    """
    conf = read_conf(file_path=file_path)
    return build_config(conf)


def get_system_instance_from_config(file_path: str):
    conf = read_conf(file_path=file_path)
    if 'system' in conf:
        system_config = SystemConfig(**conf['system'])
    else:
        raise Exception('no system config found in file')
    if 'user' in conf:
        user_config = UserConfig(**conf['user'])


def load_system_config(file_path: str):
    config = read_conf(file_path)
    return SystemConfig(**config)


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
    Builds the Config with the config data
    The function instantiate usable objects
    :param data: dict containing the raw config data
    :return: the final Config object
    """
    main_conf = Config()

    parse_auth_config(main_conf, data)
    parse_storage_config(main_conf, data)
    parse_media_downloader_config(main_conf, data)
    parse_exporter_config(main_conf, data)
    parse_streamer_config(main_conf, data)
    parse_query_fields(main_conf, data)
    parse_searcher_rule(main_conf, data)

    return main_conf


def parse_media_downloader_config(main_conf, data):
    if 'media_root_dir' in data:
        media_root_dir = data['media_root_dir']
        if 'media_download_active' in data:
            main_conf.media_download_active = data['media_download_active']
        main_conf.media_downloader = MediaDownloader(media_root_dir, main_conf.storage, main_conf.media_download_active)


def parse_streamer_config(main_conf: Config, data: dict):
    """
    Parsing of streamer options
    :param main_conf: Config
    :param data: raw config data
    """
    if main_conf.storage:
        streamer = Streamer(bearer_token=main_conf.bearer_token, storage=main_conf.storage)
        if 'streamer' in data:
            s_data = data['streamer']
            if 'verbose' in s_data:
                main_conf.streamer_verbose = s_data['verbose']
                # streamer.set_verbose(main_conf.streamer_verbose)
            if 'rules' in s_data:
                main_conf.streamer_rules = [StreamerRule(**r) for r in s_data['rules']]
        main_conf.streamer = streamer


def parse_query_fields(main_conf: Config, data: dict):
    """
    Parse query params from config
    :param main_conf: Config to populate
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


def parse_auth_config(main_conf: Config, data: dict):
    """
    Parsing of client options
    :param main_conf: Config
    :param data: raw config data
    """
    if 'bearer_token' in data:
        main_conf.bearer_token = data['bearer_token']
    if 'name' in data:
        main_conf.name = data['name']


def parse_storage_config(main_conf: Config, data: dict):
    """
    Parsing of storage options
    :param main_conf: Config
    :param data: raw config data
    """
    if 'storage' in data:
        storage = PostgresStorage(name='System Storage', **data['storage'])
        main_conf.storage = storage


def parse_exporter_config(main_conf: Config, data: dict):
    """
    Parsing of storage options
    :param main_conf: Config
    :param data: raw config data
    """
    if 'exporters' in data:
        for key, value in data['exporters'].items():
            exporter = create_exporter(key, value)
            main_conf.exporters[exporter.name] = exporter


def parse_searcher_rule(main_conf: Config, data: dict):
    if 'searcher' in data:
        data = data['searcher']
        if 'rule' in data:
            main_conf.searcher_rule = SearcherRule(**data['rule'])
        if main_conf.bearer_token and main_conf.storage:
            main_conf.searcher = Searcher(storage=main_conf.storage, bearer_token=main_conf.bearer_token)


# def create_storage_manager(main_conf: Config, main_storage_name: str) -> Optional[StorageManager]:
#     """
#     Create a storage_manager and set parameters according to config
#     :param main_conf: Config
#     :param main_storage_name: name of the main storage
#     :return: storage_manager
#     """
#     main_storage: PostgresStorage = main_conf.storages[main_storage_name]
#
#     manager = StorageManager(main_storage=main_storage,
#                              media_root_dir=main_conf.media_root_dir,
#                              download_media=main_conf.media_download)
#     for s_name in main_conf.storage_tags:
#         if s_name == main_storage_name:
#             continue
#         storage = main_conf.storages[s_name]
#         tags = main_conf.storage_tags[s_name]
#         manager.add_storage(storage=storage, tags=tags)
#     return manager


def create_exporter(name: str, data: dict):
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
    if storage_type == 'csv':
        return CSVExporter(name=name, **data)
