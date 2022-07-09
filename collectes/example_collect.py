import json
import logging
import os

from restweetution.models.config.query_params_config import MEDIUM_CONFIG
from restweetution.storage import FileStorage

if __name__ == "__main__":
    logging.basicConfig()
    logging.root.setLevel(logging.INFO)
    with open(os.getenv("CREDENTIALS"), "r") as f:
        token = json.load(f).get('token')
    config = {
        'token': token,
        'tweets_storages': [
            FileStorage(root=os.path.join(os.getenv('ROOT_PATH'), 'Data'), tags=['Rule2']),
            # config syntax:
            # {
            #     'storage': {
            #         'type': 'file',
            #         'root': os.path.join(os.getenv('ROOT_PATH')),
            #         'tags': ['GR']
            #     }
            # }
            # object syntax
            # SSHStorage(root='/home/felixalie/tweets',
            #            host='ceres.huma-num.fr',
            #            user='felixalie',
            #            password=os.getenv('SSH_PWD'),
            #            tags: ['ZemmourVsMelenchon'])
        ],
        'media_storages': [
            # no tags mean all media storages will be stored directly here
            FileStorage(root=os.path.join(os.getenv('ROOT_PATH'), 'GrandRemplacementMedia'), max_size=1000, tags=['GR']),
        ],
        'verbose': True,
        'tweet_config': MEDIUM_CONFIG.dict(),
        'average_hash': True
    }
    s = Streamer(config)
    s.set_stream_rules({'Rule2': '(Johnny) OR (Depp) OR (MELANCHON)'})
    s.collect()
