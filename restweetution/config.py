import json
import os

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
