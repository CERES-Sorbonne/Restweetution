import os
from collections import defaultdict
from pathlib import Path
from typing import List, DefaultDict

import aiofiles
from aiocsv import AsyncWriter
from numpy.core.defchararray import isnumeric

from restweetution.models.storage.custom_data import CustomData
from restweetution.storages.exporter.exporter import Exporter

STORAGE_TYPE = 'csv'


class CSVExporter(Exporter):
    def __init__(self, name, root_dir, **kwargs):
        super().__init__(name)
        self._root = Path(root_dir)
        self.root_dir = root_dir

    def get_config(self):
        return {
            'type': STORAGE_TYPE,
            'name': self.name,
            'root_dir': self.root_dir
        }

    async def save_custom_datas(self, datas: List[CustomData]):
        key_group: DefaultDict[str, List[CustomData]] = defaultdict(list)
        for data in datas:
            key_group[data.key].append(data)

        for key in key_group:
            rows = sorted(key_group[key], key=lambda x: int(x.id) if isnumeric(x.id) else x.id)
            min_id = rows[0].id
            max_id = rows[-1].id
            filename = key + min_id + '-' + max_id + '.csv'
            path = self._root / filename
            path = Path(self.uniquify(path))
            async with aiofiles.open(path, mode="w", encoding="utf-8", newline="") as afp:
                writer = AsyncWriter(afp, dialect="excel")
                await writer.writerows([[self._parse(r2) for r2 in r1.data.values()] for r1 in rows])

    @staticmethod
    def uniquify(path):
        filename, extension = os.path.splitext(path)
        counter = 1

        while os.path.exists(path):
            path = filename + " (" + str(counter) + ")" + extension
            counter += 1

        return path

    @staticmethod
    def _parse(value):
        if isinstance(value, list):
            return '|'.join(value)
        return value
