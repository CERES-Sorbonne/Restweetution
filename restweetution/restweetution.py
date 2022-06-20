from typing import List

from restweetution.collectors import AsyncStreamer
from restweetution.models.storage_config import StorageConfig
from restweetution.storage.async_storage_manager import AsyncStorageManager
from restweetution.utils import resolve_storage


class Restweetution:
    def __init__(self):
        self._storage_manager = AsyncStorageManager()
        self._streamer = AsyncStreamer(self._storage_manager)

    def set_streamer_config(self, config: dict):
        self._streamer.load_config(config)

    def set_storages(self, storage_configs: List[dict]):
        self.remove_storages()
        self.add_storages(storage_configs)

    def add_storages(self, storage_configs: List[dict]):
        for storage_config in storage_configs:
            if isinstance(storage_config, dict):
                storage_config = StorageConfig(**storage_config)

            if isinstance(storage_config.storage, dict):
                storage_config.storage = resolve_storage(storage_config.storage)

            self._storage_manager.add_storage(storage=storage_config.storage,
                                              tags=storage_config.tags)

    def remove_storages(self, names: List[str] = None):
        self._storage_manager.remove_storages(names)
