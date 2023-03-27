import asyncio
from typing import List

from restweetution.data_view.data_view import DataView
from restweetution.models.bulk_data import BulkData
from restweetution.models.storage.custom_data import CustomData
from restweetution.storages.exporter.exporter import Exporter
from restweetution.utils import fire_and_forget


class ViewExporter:
    def __init__(self, view: DataView, exporter: Exporter):
        self._view = view
        self._exporter = exporter

    def export(self, bulk_data: BulkData, key: str, only_ids: List[str] = None, **kwargs):
        res = self._view.compute(bulk_data, only_ids=only_ids, **kwargs)
        res = [CustomData(id=r[self._view.id_field()], key=key, data=r) for r in res]
        return fire_and_forget(self._exporter.save_custom_datas(res))
