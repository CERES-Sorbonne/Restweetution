import json
import logging
import os

from restweetution.collectors import Streamer
from restweetution.models.examples_config import MEDIUM_CONFIG
from restweetution.storage import FileStorage, SSHFileStorage

if __name__ == "__main__":
    logging.basicConfig()
    logging.root.setLevel(logging.INFO)
    with open(os.getenv("CREDENTIALS"), "r") as f:
        token = json.load(f).get('token')
    config = {
        'token': token,
        'tweets_storages': [
            {
                'storage': FileStorage(root=os.path.join(os.getenv('ROOT_PATH'), 'GrandRemplacement')),
                'tags': ['GR']
            }
            # },
            # {
            #     'storage': SSHFileStorage(root='/home/felixalie/tweets',
            #                               host='ceres.huma-num.fr',
            #                               user='felixalie',
            #                               password=os.getenv('SSH_PWD')),
            #     'tags': ['ZemmourVsMelenchon']
            # }
        ],
        'media_storages': [
            {
                'storage': FileStorage(root=os.path.join(os.getenv('ROOT_PATH'), 'GrandRemplacementMedia'), max_size=1000),
                'tags': ['GR']
            },
            # no tags mean all media storages will be stored directly here
        ],
        'verbose': True,
        'tweet_config': MEDIUM_CONFIG.dict(),
        'average_hash': True
    }
    s = Streamer(config)
    s.add_rule('(Grand Remplacement) OR (Grand Declassement) OR (Grand remplaçement)', 'GR')
    s.collect()
