import asyncio
import datetime
import os
import time

from restweetution import config_loader
from restweetution.storages.extractor import Extractor


async def main():
    conf = config_loader.load_system_config(os.getenv('SYSTEM_CONFIG'))
    postgres = conf.build_storage()

    date_from = datetime.datetime(2021, 8, 31, 22, 0, tzinfo=datetime.timezone.utc)
    date_to = datetime.datetime(2022, 6, 1, 22, 0, tzinfo=datetime.timezone.utc)
    extractor = Extractor(postgres)
    run = True
    offset = 0
    limit = 1000
    while run:
        old = time.time()
        res = await postgres.get_tweets(rule_ids=[78], date_from=date_from, date_to=date_to, offset=offset, limit=limit)
        print(f'GET: { len(res)} tweets: {time.time() - old} seconds')
        inter = time.time()
        bulk = await extractor.expand_tweets(res)
        print(f'Extract {time.time() - inter} seconds (total: {time.time() - old})')

        run = len(res) > 0
        offset += limit
    # print(res)

loop = asyncio.get_event_loop()
loop.run_until_complete(main())

    # extractor = Extractor(postgres)
    # res = await extractor.expand_tweets(res)
    # for k in res.__dict__:
    #     if hasattr(res.__dict__[k], '__len__'):
    #         print(k, ': ', len(res.__dict__[k]))

    # elastic = conf.build_elastic()
    # view = RowView(elastic)
    #
    # res = view.compute(res, 'test')
    # for r in res:
    #     print(r.data['rule_tags'])


loop = asyncio.get_event_loop()
loop.run_until_complete(main())
