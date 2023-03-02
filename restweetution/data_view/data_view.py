from abc import ABC
from typing import List, Dict

from restweetution.models.bulk_data import BulkData
from restweetution.storages.exporter.exporter import Exporter
from restweetution.storages.storage import Storage


class DataUnit(dict):
    def __init__(self, id_: str, **kwargs):
        super().__init__(**kwargs)
        self['id'] = id_

    def id(self):
        return self['id']


class DataView(ABC):
    @staticmethod
    def compute(bulk_data: BulkData, only_ids: List[str] = None, **kwargs) -> List[Dict]:
        raise NotImplementedError('compute not implemented')

    @staticmethod
    def id_field() -> str:
        raise NotImplementedError('Please declare a field to be used as id')
        # example: return 'id'

