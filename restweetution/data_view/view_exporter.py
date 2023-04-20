import asyncio
from typing import List

from restweetution.data_view import TweetView2
from restweetution.data_view.data_view2 import DataView2
from restweetution.models.bulk_data import BulkData
from restweetution.models.linked.linked import Linked
from restweetution.models.linked.linked_tweet import LinkedTweet
from restweetution.models.storage.custom_data import CustomData
from restweetution.storages.exporter.exporter import Exporter


class ViewExporter:
    def __init__(self, view: DataView2, exporter: Exporter):
        self._view = view
        self._exporter = exporter

    def export(self, key: str, linked: List[Linked], fields: List[str] = None):
        res = self._view.compute(linked, fields)
        res = [CustomData(id=r.id(), key=key, data=r) for r in res.view]
        return asyncio.create_task(self._exporter.save_custom_datas(res))
