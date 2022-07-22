import asyncio
import logging
import os

import restweetution.config as config
from restweetution.storage.media_downloader import MediaDownloader
from restweetution.models.twitter import Media

logging.basicConfig()
logging.root.setLevel(logging.INFO)

main_conf = config.get_config_from_file(os.getenv('CONFIG'))


async def launch():
    storage = main_conf.storages[0]
    # res = await storage.get_places()
    # res = await BaseExtractor.get_users(main_conf.storage_tweet_storages)
    # update = twitter.Media(media_key='3_1550171291163975683', type='photo', sha1='test22111')
    # res = await storage.update_medias([update])
    # print(res)
    # print(len(res))
    d = MediaDownloader(root='/Users/david/Restweetution/collectes', storage=storage)
    media = Media(media_key='3_1550132976524341250', type='photo', url='https://pbs.twimg.com/media/FYMtuqxaMAIf9Ok.jpg')
    await d.save_medias([media])



loop = asyncio.get_event_loop()
loop.create_task(launch())
try:
    loop.run_forever()
except KeyboardInterrupt as e:
    pass
