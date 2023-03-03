import asyncio
import json
import os

from restweetution import config_loader


async def main():
    conf = config_loader.load_system_config(os.getenv('SYSTEM_CONFIG'))
    storage = conf.build_storage()

    to_save = []

    async for res in storage.get_collected_tweets_stream(
            rule_ids=[348, 333, 341, 340, 334, 338, 345, 337, 339, 335, 336, 342, 331, 343, 334, 332],
            direct_hit=True):
        res = [r.tweet for r in res]
        tweets = [tweet for tweet in res if tweet.lang == 'fr']
        data = [{"id": tweet.id,
                 "text": tweet.text,
                 "created_at": tweet.created_at,
                 "author_id": tweet.author_id,
                 "retweet_count": tweet.public_metrics.retweet_count
                 } for tweet in tweets]

        to_save.extend(data)
        print(len(to_save))

    with open('julien-result.json', 'w') as f:
        json.dump(to_save, f)

asyncio.run(main())
