import asyncio
import time
from datetime import datetime

from restweetution.models.storage.custom_data import CustomData
from restweetution.storages.exporter.exporter import Exporter


class StatusView:
    def __init__(self, storage_manager, output: Exporter):
        self._storage = storage_manager
        self._output = output
        self._task = None

    def update(self, interval: int):
        self._task = asyncio.create_task(self._update_task(interval))

    async def _update_task(self, interval: int):
        while True:
            timestamp = round(time.time() * 1000)
            status = self._storage.get_status()
            status['timestamp'] = datetime.now().utcnow()
            # print(status)
            status_data = CustomData(key='status_data', id=str(timestamp), data=status)
            await self._output.save_custom_datas([status_data])
            await asyncio.sleep(interval)

    def stop(self):
        self._task.cancel()
