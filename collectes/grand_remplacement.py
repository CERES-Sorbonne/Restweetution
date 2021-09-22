import json
from restweetution.collectors import Streamer

if __name__ == "__main__":
    with open(r"/home/tyra/Documents/CERES/credentials_pro.json", "r") as f:
        token = json.load(f).get('token')
    config = {
        'token': token,
        'tweet_storage': {
            "root_directory": r"C:\Users\Orion\Documents\OutputTweets",
            "max_size": 1000
        },
        'media_storage': {
            "root_directory": r"C:\Users\Orion\Documents\OutputTweets\media",
            "max_size": 1000
        }
    }
    s = Streamer(config)
    s.collect()