from abc import ABC

from restweetution.storages.exporter.exporter import Exporter
from restweetution.storages.storage import Storage


class DataUnit(dict):
    def __init__(self, id_: str, **kwargs):
        super().__init__(**kwargs)
        self['id'] = id_

    def id(self):
        return self['id']


class DataView(ABC):
    def __init__(self, name: str, in_storage: Storage, out_storage: Exporter):
        self._view_name = name
        self.input = in_storage
        self.output = out_storage

    async def load(self, **kwargs):
        pass

    async def save(self, **kwargs):
        pass
