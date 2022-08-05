import asyncio
import logging
import os
import restweetution.config as config

logging.basicConfig()
logging.root.setLevel(logging.INFO)

main_conf = config.get_config_from_file(os.getenv('CONFIG'))


async def launch():
    streamer = main_conf.streamer
    # print(main_conf.streamer_rules)
    await streamer.collect(rules=main_conf.streamer_rules, fields=main_conf.query_fields)

loop = asyncio.get_event_loop()
loop.create_task(launch())
try:
    loop.run_forever()
except KeyboardInterrupt as e:
    pass
