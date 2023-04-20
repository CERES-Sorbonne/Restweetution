import asyncio
from typing import List

from restweetution.data_view.data_view2 import DataView2
from restweetution.models.bulk_data import BulkData
from restweetution.models.storage.custom_data import CustomData
from restweetution.storages.exporter.exporter import Exporter


class ViewExporter:
    def __init__(self, view: DataView2, exporter: Exporter):
        self._view = view
        self._exporter = exporter

    def export(self, bulk_data: BulkData, key: str, only_ids: List[str] = None, **kwargs):
        res = self._view.compute(bulk_data, only_ids=only_ids, **kwargs)
        res = [CustomData(id=r.id(), key=key, data=r) for r in res.view]
        return asyncio.create_task(self._exporter.save_custom_datas(res))
