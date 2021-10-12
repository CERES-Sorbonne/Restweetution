import json
import logging
import os

from restweetution.collectors import Streamer
from restweetution.models.examples_config import MEDIUM_CONFIG

if __name__ == "__main__":
    logging.basicConfig()
    logging.root.setLevel(logging.INFO)
    with open(os.getenv("CREDENTIALS"), "r") as f:
        token = json.load(f).get('token')
    config = {
        'token': token,
        'tweets_storages': [{
            "root_directory": os.getenv('ROOT_PATH'),
            "max_size": 1000
        }],
        # 'media_storages': {
        #     "root_directory": r"C:\Users\Orion\Documents\OutputTweets\media",
        #     "max_size": 1000
        # },
        'verbose': True,
        'tweet_config': MEDIUM_CONFIG.dict()
    }
    s = Streamer(config)
    s.collect()