import asyncio
import datetime
import os
import time

from restweetution import config_loader
from restweetution.data_view.row_view import RowView
from restweetution.data_view.view_exporter import ViewExporter
from restweetution.storages.extractor import Extractor


async def main():
    conf = config_loader.load_system_config(os.getenv('SYSTEM_CONFIG'))
    postgres = conf.build_storage()

    date_from = datetime.datetime(2021, 9, 1, 0, 0, tzinfo=datetime.timezone.utc)
    date_to = datetime.datetime(2022, 6, 1, 0, 0, tzinfo=datetime.timezone.utc)
    rule_ids = [2]
    extractor = Extractor(postgres)

    view_exporter = ViewExporter(view=RowView(), exporter=conf.build_elastic())
    old = time.time()
    async for res in postgres.get_collected_tweets_stream(rule_ids=rule_ids, date_from=date_from, date_to=date_to):
        print(f'GET: { len(res)} tweets: {time.time() - old} seconds')
        inter = time.time()
        bulk = await extractor.expand_collected_tweets(res)
        print(f'Extract {time.time() - inter} seconds (total: {time.time() - old})')
        inter = time.time()
        # await view_exporter.export(bulk_data=bulk, key='debug', only_ids=[r.tweet_id for r in res])
        print(f'Send to dashboard {time.time() - inter} seconds (total: {time.time() - old})')
        old = time.time()


loop = asyncio.get_event_loop()
loop.run_until_complete(main())
