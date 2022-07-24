import asyncio
import logging
import os

import restweetution.config as config
from restweetution.models.storage.twitter import Media
from restweetution.storage.storages.elastic_storage.elastic_storage import ElasticStorage
from restweetution.storage.storages.postgres_storage.postgres_storage import PostgresStorage

logging.basicConfig()
logging.root.setLevel(logging.INFO)

main_conf = config.get_config_from_file(os.getenv('CONFIG'))


async def launch():
    postgres_storage: PostgresStorage = main_conf.storages['local_postgres']
    elastic_storage: ElasticStorage = main_conf.storages['ceres_elastic']

    res = await elastic_storage.get_medias()

    to_save = []
    for m in res:
        m.sha1 = 'hehe'
        m.type = 'photo'
        to_save.append(Media(media_key=m.media_key))

    await elastic_storage.update_medias(to_save, delete=['sha1'])

    # data = CustomData(key='test', id=3, data={'CHOUPI': True})
    # data2 = CustomData(key='test', id=1, data={'Luffy': True})
    # await storage.save_custom_datas([data, data2])
    # res = await storage.get_custom_datas(key='test')
    # print(res)
    # await storage.del_custom_data(key='test')
    # await storage.del_custom_data(key='other')

    # for x in await storage.get_tweets():
    #     print(x.attachments)

    # view = ElasticView(in_storage=postgres_storage, out_storage=elastic_storage)
    # await view.load()
    # await view.save()

    # res = await elastic.get_custom_datas('elastic')
    # print(len(res))

    # await elastic_storage.del_custom_datas('elastic')


asyncio.run(launch())
