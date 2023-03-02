import json

import yaml

from restweetution.models.config.system_config import SystemConfig


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
        raise ValueError('Config file path is empty ! You can set the path with SYSTEM_CONFIG=<path>')
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


# def create_exporter(name: str, data: dict):
#     """
#     Create a storage and set parameters according to config
#     :param name: name of the storage, used for identification
#     :param data: raw config data
#     :return: storage
#     """
#     storage_type = data['type']
#     if storage_type == 'elastic':
#         return ElasticStorage(name=name, **data)
#     if storage_type == 'postgres':
#         return PostgresStorage(name=name, **data)
#     if storage_type == 'csv':
#         return CSVExporter(name=name, **data)
