import asyncio
import logging
import os

from sqlalchemy import select

import restweetution.config as config
from restweetution.data_view.row_view import RowView
from restweetution.models.storage.custom_data import CustomData
from restweetution.storages.elastic_storage.elastic_storage import ElasticStorage
from restweetution.storages.exporter.csv_exporter import CSVExporter
from restweetution.storages.postgres_storage.postgres_storage import PostgresStorage

logging.basicConfig()
logging.root.setLevel(logging.INFO)

main_conf = config.get_config_from_file(os.getenv('CONFIG'))


async def launch():

    postgres_storage: PostgresStorage = main_conf.storages['local_postgres']
    exporter = CSVExporter(root_path='/Users/david/Restweetution/collectes')

    fields = ['id', 'author_username', 'lang', 'annotations', 'media_sha1s']
    view = RowView(in_storage=postgres_storage, out_storage=exporter, fields=fields)

    res = await view.load()
    await view.save_rows(res)






    elastic_storage: ElasticStorage = main_conf.storages['ceres_elastic']

    # exporter = CSVExporter(root_path='/Users/david/Restweetution/collectes')
    # await exporter.save_custom_datas([
    #     CustomData(id='100', key='tweet', data={1: 1, 2: ['lala', 'lolo'], 3: 3}),
    #     CustomData(id='104', key='tweet', data={1: 3, 2: None, 3: 1}),
    #     CustomData(id='300', key='tweet', data={1: 9, 2: 2, 3: 5}),
    #     CustomData(id='550', key='tweet', data={1: 4, 2: 5, 3: 0})
    # ])



    # res = await postgres_storage.update_error()
    # for r in res:
    #     print(r)
    # async with postgres_storage._engine.begin() as conn:
    #     stmt = select(models)
    # for r in res:
    #     print(r.data)
    # res = [t for t in res if t.context_annotations]
    #
    # dd = None
    # for r in res:
    #     print(r.id)
    #     print(r.context_annotations)
    #     r.context_annotations = []
    #     dd = RestTweet(id=r.id)
    #     dd.text = 'troll'
    # await postgres_storage.save_tweets([dd])
    # res = await postgres_storage.get_tweets(order='id')
    # print(res[0].id)
    # data2 = CustomData(key='test', data={'Luffy': True})
    # await postgres_storage.save_custom_datas([data2])
    # res = await storage.get_custom_datas(key='test')
    # print(res)
    # await storage.del_custom_data(key='test')
    # await storage.del_custom_data(key='other')

    # for x in await storage.get_tweets():
    #     print(x.attachments)

    # view = ElasticView(in_storage=postgres_storage, out_storage=elastic_storage)
    # await view.load()
    # await view.save()

    # datas = await elastic_storage.get_custom_datas(key='elastic')
    # updated = []
    # for d in datas:
    #     d.data['photo_url'] = 'https://cvlaval.com/sites/default/files/carousel/chat-1.jpg'
    # await elastic_storage.save_custom_datas(datas=updated)
    # res = await elastic.get_custom_datas('elastic')
    # print(len(res))

    # await elastic_storage.del_custom_datas('elastic')


asyncio.run(launch())
