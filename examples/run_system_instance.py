import asyncio
import logging
import os
from restweetution import config_loader
from restweetution.instances.system_instance import SystemInstance

logging.basicConfig()
logging.root.setLevel(logging.INFO)


system_config = config_loader.load_system_config(os.getenv('SYSTEM_CONFIG'))


async def launch():
    instance = SystemInstance(system_config=system_config)
    await instance.load_user_configs()

    user = list(instance.user_instances.values())[0]

    print('rules: ', user._streamer.get_rules())
    print('end launch')

loop = asyncio.get_event_loop()
loop.create_task(launch())
try:
    loop.run_forever()
except KeyboardInterrupt as e:
    pass
