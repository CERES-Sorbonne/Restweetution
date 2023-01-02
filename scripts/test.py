import asyncio
import datetime
import os

from restweetution import config_loader
from restweetution.data_view.row_view import RowView
from restweetution.storages.extractor import Extractor


async def main():
    conf = config_loader.load_system_config(os.getenv('SYSTEM_CONFIG'))
    postgres = conf.build_storage()

    date_from = datetime.datetime.now() - datetime.timedelta(hours=10)
    date_to = datetime.datetime.now() - datetime.timedelta(hours=0)
    # res = await postgres.get_tweets_count(rule_ids=[294])
    # res = await postgres.get_tweets_count(date_from=date_from, date_to=date_to)
    res = await postgres.get_tweets_raw(rule_ids=[1], date_from=date_from, date_to=date_to)
    print(len(res))
    # print(res)
    return
    extractor = Extractor(postgres)
    res = await extractor.expand_tweets(res)
    for k in res.__dict__:
        if hasattr(res.__dict__[k], '__len__'):
            print(k, ': ', len(res.__dict__[k]))

    elastic = conf.build_elastic()
    view = RowView(elastic)

    res = view.compute(res, 'test')
    # for r in res:
    #     print(r.data['rule_tags'])

loop = asyncio.get_event_loop()
loop.run_until_complete(main())
