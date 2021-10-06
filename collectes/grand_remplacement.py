import json
import logging
from restweetution.collectors import Streamer

if __name__ == "__main__":
    logging.basicConfig()
    logging.root.setLevel(logging.INFO)
    with open(r"C:\Users\Orion\Documents\Projets\CERES\credentials_pro.json", "r") as f:
        token = json.load(f).get('token')
    config = {
        'token': token,
        'tweets_storages': [{
            "root_directory": r"C:\Users\Orion\Documents\OutputTweets",
            "max_size": 1000
        }],
        # 'media_storages': {
        #     "root_directory": r"C:\Users\Orion\Documents\OutputTweets\media",
        #     "max_size": 1000
        # },
        'verbose': True
    }
    s = Streamer(config)
    s.collect()