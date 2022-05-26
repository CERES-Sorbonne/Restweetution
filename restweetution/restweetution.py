from restweetution.collectors import AsyncStreamer
from restweetution.storage.async_storage_manager import AsyncStorageManager


class Restweetution:
    def __init__(self):
        self._storage_manager = AsyncStorageManager()
        self._streamer = AsyncStreamer(self._storage_manager)
