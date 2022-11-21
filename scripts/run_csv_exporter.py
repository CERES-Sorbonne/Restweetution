import asyncio
import logging
import os

import restweetution.config_loader as config
from restweetution.data_view.row_view import RowView

logging.basicConfig()
logging.root.setLevel(logging.INFO)

main_conf = config.get_config_from_file(os.getenv('CONFIG'))


async def launch():
    exporter = main_conf.exporters['csv']

    fields = ['id', 'author_username', 'lang', 'annotations', 'media_sha1s']
    view = RowView(in_storage=main_conf.storage, out_storage=exporter, fields=fields)

    res = await view.load()
    await view.save_rows(res)

asyncio.run(launch())
