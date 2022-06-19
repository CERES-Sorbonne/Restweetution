import json
import os

import yaml

from restweetution.models.stream_config import StreamConfig
from restweetution.storage.elastic_storage.elastic_storage import ElasticTweetStorage

config = {}


def get_config():
    global config
    if config == {}:
        config = load_config()
    return config


def load_config():
    with open(os.getenv("CREDENTIALS"), "r") as f:
        data = json.load(f)
        return {
            "token": data['token'],
            "elastic_config": data['elastic_config']
        }


def read_conf(path_to_config_file: str):
    if path_to_config_file.split('.')[-1] == 'json':
        try:
            with open(path_to_config_file, 'r') as f:
                return StreamConfig(**json.load(f))
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON provided, the following error occurred trying to open the config: {e}")

    elif path_to_config_file.split('.')[-1] == 'yaml':
        try:
            with open(path_to_config_file, 'r') as f:
                return StreamConfig(**yaml.safe_load(f))
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML provided, the following error occurred trying to open the config: {e}")
    else:
        raise ValueError("Invalid config provided")
