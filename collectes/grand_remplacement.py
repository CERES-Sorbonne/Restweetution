import json
import logging
import os

from restweetution.collectors import Streamer
from restweetution.models.examples_config import MEDIUM_CONFIG
from restweetution.storage import FileStorage

if __name__ == "__main__":
    logging.basicConfig()
    logging.root.setLevel(logging.INFO)
    with open(os.getenv("CREDENTIALS"), "r") as f:
        token = json.load(f).get('token')
    config = {
        'token': token,
        'tweets_storages': [
            {
                'storage': FileStorage(root=os.getenv('ROOT_PATH')),
                'tags': ['PMA', 'GR', 'ZemmourVsMelenchon']
            },
            # {
            #     'storage': SQLLite(host='', db='', user='', password=''),
            #     'tags': ['GR'],
            #     # tables "tweets", "rules", "users", "tweets_to_images", will be created if not existing
            # }
        ],
        'media_storages': [
            {
                'storage': FileStorage(root=os.path.join(os.getenv('ROOT_PATH'), 'media')),
            },
            # no tags mean all media storages will be stored directly here
        ],
        'verbose': True,
        'tweet_config': MEDIUM_CONFIG.dict(),
        'average_hash': True
    }
    s = Streamer(config)
    s.collect()
