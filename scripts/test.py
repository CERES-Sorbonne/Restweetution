import asyncio
import datetime
import os
import time

from restweetution import config_loader
from restweetution.data_view.row_view import RowView
from restweetution.data_view.view_exporter import ViewExporter
from restweetution.models.storage.queries import CollectedTweetQuery
from restweetution.storages.elastic_storage.elastic_storage import ElasticStorage
from restweetution.storages.exporter.csv_exporter import CSVExporter
from restweetution.storages.extractor import Extractor
from restweetution.tasks.tweet_export_task import TweetExportTask

elastic: ElasticStorage


async def main():
    global elastic
    conf = config_loader.load_system_config(os.getenv('SYSTEM_CONFIG'))
    postgres = conf.build_storage()
    elastic = conf.build_elastic_exporter()
    extractor = Extractor(postgres)

    csv = CSVExporter('tweet', '/Users/david/Restweetution/csv_dump')

    date_from = datetime.datetime(2021, 9, 1, 0, 0, tzinfo=datetime.timezone.utc)
    date_to = datetime.datetime(2022, 6, 1, 0, 0, tzinfo=datetime.timezone.utc)
    rule_ids = [2]

    res = await postgres.get_collected_tweets(rule_ids=rule_ids)
    bulk = await extractor.expand_collected_tweets(res)

    view_exporter = ViewExporter(RowView(), csv)
    await view_exporter.export(bulk_data=bulk, key='felix-sha1s', only_ids=[r.tweet_id for r in res], fields=['media_sha1s'])


asyncio.run(main())
