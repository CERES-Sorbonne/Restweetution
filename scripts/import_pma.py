import asyncio
import csv
import os
from collections import defaultdict

from restweetution import config_loader
from restweetution.data_view.data_view import DataUnit
from restweetution.models.twitter import Tweet, User


async def launch():
    conf = config_loader.load_system_config(os.getenv('SYSTEM_CONFIG'))

    with open('/Users/david/Restweetution/collectes/sous_corpus_pma_with_sha1_and_ahash8.csv', 'r') as csvfile:
        csvreader = csv.reader(csvfile)
        fields = None
        tweets = []
        tweets_dict = defaultdict(int)

        for row in csvreader:
            if not fields:
                fields = row
            else:
                row_dict = {fields[k]: row[k] for k in range(len(fields))}
                # print(row_dict)
                tweet_id = row_dict['tweet_id']
                tweets.append(row_dict)
                tweets_dict[tweet_id] += 1
                # tweet = Tweet(id=row_dict['tweet_id'], author_id=row_dict['user_id'], text=row_dict['text'], created_at)
                # user = User(id=row_dict['user_id'], username=row_dict['user_name'])

        print(len(tweets))
        print(len({t['tweet_id'] for t in tweets}))
        # print(tweets)
        tweet_to_sha1 = defaultdict(set)
        for t in tweets:
            tweet_to_sha1[t['id']].add(t['sha1'])

        # print(tweet_to_sha1)

        unique = {}
        for t in tweets:
            t['sha1'] = list(tweet_to_sha1[t['id']])
            unique[t['id']] = t

        to_save = []
        for tid, tweet in unique:
            data = DataUnit(id_=tid, )

asyncio.run(launch())
