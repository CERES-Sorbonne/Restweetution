import asyncio
import os
import time

from restweetution import config_loader
from restweetution.models.bulk_data import BulkData
from restweetution.models.storage.downloaded_media import DownloadedMedia
from restweetution.models.twitter import Media
from restweetution.storages.elastic_storage.elastic_storage import ElasticStorage
from restweetution.storages.postgres_storage.postgres_storage import PostgresStorage

elastic: ElasticStorage


async def main():
    global elastic
    conf = config_loader.load_system_config(os.getenv('SYSTEM_CONFIG'))

    # server = SSHTunnelForwarder(('ceres.huma-num.fr', 22),
    #                             ssh_private_key=r'/Users/david/.ssh/id_ed25519',
    #                             ssh_username="davidg",
    #                             remote_bind_address=('127.0.0.1', 5432),
    #                             # logger=create_logger(loglevel=1)  # Makes processes being ran displayed
    #                             )
    # server.start()

    storage = conf.build_storage()

    old = time.time()
    async for res in storage.get_collected_tweets_stream(rule_ids=[78]):
        print(f'time: {time.time() - old}')
        old = time.time()



    # server.stop()

    # postgres = conf.build_storage()
    # elastic = conf.build_elastic_exporter()
    # extractor = Extractor(postgres)
    #
    # csv = CSVExporter('tweet', '/Users/david/Restweetution/csv_dump')
    #
    # date_from = datetime.datetime(2021, 9, 1, 0, 0, tzinfo=datetime.timezone.utc)
    # date_to = datetime.datetime(2022, 6, 1, 0, 0, tzinfo=datetime.timezone.utc)
    # rule_ids = [2]
    #
    # res = await postgres.get_collected_tweets(rule_ids=rule_ids)
    # bulk = await extractor.expand_collected_tweets(res)
    #
    # view_exporter = ViewExporter(RowView(), csv)
    # await view_exporter.export(bulk_data=bulk, key='felix-sha1s', only_ids=[r.tweet_id for r in res], fields=['media_sha1s'])


asyncio.run(main())
