from abc import ABC
from typing import List, Dict

from restweetution.models.bulk_data import BulkData
from restweetution.models.storage.custom_data import CustomData
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
        self._is_loaded = False
        self.datas: Dict[str, DataUnit] = {}

    async def load(self):
        pass

    async def save(self):
        to_save = []
        for d in self._get_datas():
            to_save.append(self._custom_data(d))
        await self.output.save_custom_datas(to_save)

    async def add(self, bulk_data: BulkData):
        pass

    def _custom_data(self, data: DataUnit):
        return CustomData(key=self._view_name, id=data['id'], data=data)

    def _get_datas(self) -> List[DataUnit]:
        return list(self.datas.values())

    def _add_datas(self, datas: List[DataUnit]):
        for d in datas:
            self.datas[d.id()] = d
