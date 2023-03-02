import asyncio
import datetime
import json
import os
from pathlib import Path

from restweetution import config_loader
from restweetution.collectors.response_parser import parse_includes
from restweetution.models.bulk_data import BulkData
from restweetution.models.rule import Rule
from restweetution.models.twitter import TweetResponse

from os import listdir
from os.path import isfile, join

tweet_dir = '/home/felixalie/collectes_twitter/IVG/tweets'

tag_to_rule = {
    'ZM': 78,
    'IVG': 79
}

conf = config_loader.load_system_config(os.getenv('SYSTEM_CONFIG'))


def parse_data(tweet_res: TweetResponse, created_at):
    bulk_data = BulkData()

    # Add collected tweet
    tweet = tweet_res.data
    tweet.created_at = created_at
    bulk_data.add_tweets([tweet])

    # Add includes
    includes = tweet_res.includes
    bulk_data.add(**parse_includes(includes))

    # Get the full rule from the id in matching_rules
    rules = [Rule(id=tag_to_rule[r.tag], tag=r.tag) for r in tweet_res.matching_rules]

    assert len(rules) > 0

    # Mark the tweets as collected by the rules
    collected_at = tweet.created_at
    for rule in rules:
        rule.add_direct_tweets(tweet_ids=[tweet.id], collected_at=collected_at)
        if includes and includes.tweets:
            tweet_ids = [t.id for t in includes.tweets]
            rule.add_includes_tweets(tweet_ids=tweet_ids, collected_at=collected_at)

    bulk_data.add_rules(rules)
    return bulk_data


async def launch():
    storage = conf.build_storage()
    files = [f for f in listdir(tweet_dir) if isfile(join(tweet_dir, f))]

    base = Path(tweet_dir)

    for file in files:
        created_at = datetime.datetime.fromtimestamp(os.path.getctime(base/file))
        with open(base / file, 'r') as f:
            data = json.load(f)
            resp = TweetResponse(**data)
            bulk = parse_data(resp, created_at)
            await storage.save_bulk(bulk)

asyncio.run(launch())
