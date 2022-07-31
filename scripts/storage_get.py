import asyncio
import logging
import os

import restweetution.config as config
from restweetution.storages.elastic_storage.elastic_storage import ElasticStorage
from restweetution.storages.postgres_storage.postgres_storage import PostgresStorage

logging.basicConfig()
logging.root.setLevel(logging.INFO)

main_conf = config.get_config_from_file(os.getenv('CONFIG'))


async def launch():
    postgres_storage: PostgresStorage = main_conf.storages['local_postgres']
    elastic_storage: ElasticStorage = main_conf.storages['ceres_elastic']

    # searcher = Searcher(storage=main_conf.storage_manager, bearer_token=main_conf.client_token)
    # await searcher.search_loop_recent(query="#cat", max_results=100, expansions=['referenced_tweets.id'])
    # res = await postgres_storage.get_medias(ids=['7_1551705587511074816'])
    # print(res[0].url is None)
    # res = await elastic_storage.get_medias()

    # res = await postgres_storage.get_rules()
    res = await postgres_storage.get_tweets(sort_by='id', id_stop='1553846860300828673')
    for r in res:
        print(r.id)
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
