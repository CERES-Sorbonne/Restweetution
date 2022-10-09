import asyncio
import logging
import os

import restweetution.config_loader as config
from restweetution.data_view.row_view import RowView
from restweetution.storages.exporter.csv_exporter import CSVExporter
from restweetution.storages.postgres_storage.postgres_storage import PostgresStorage

logging.basicConfig()
logging.root.setLevel(logging.INFO)

main_conf = config.get_config_from_file(os.getenv('CONFIG'))


async def launch():

    postgres_storage: PostgresStorage = main_conf.storages['local_postgres']
    exporter = main_conf.storages['csv']

    fields = ['id', 'author_username', 'lang', 'annotations', 'media_sha1s']
    view = RowView(in_storage=postgres_storage, out_storage=exporter, fields=fields)

    res = await view.load()
    await view.save_rows(res)

asyncio.run(launch())
