from abc import ABC
from typing import List

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
    def __init__(self, exporter: Exporter):
        self.exporter = exporter

    @staticmethod
    def compute(bulk_data: BulkData, key: str, only_ids: List[str] = None):
        raise NotImplemented('compute not implemented')

