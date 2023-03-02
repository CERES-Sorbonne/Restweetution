import os
from collections import defaultdict
from typing import List, DefaultDict

import aiofiles
from aiocsv import AsyncWriter
from aiopath import AsyncPath

from restweetution.models.storage.custom_data import CustomData
from restweetution.storages.exporter.exporter import FileExporter

STORAGE_TYPE = 'csv'


class CSVExporter(FileExporter):
    async def clear_key(self, key: str):
        path = self.get_root() / key
        await path.unlink(missing_ok=True)

    def get_root(self) -> AsyncPath:
        return self._root

    def __init__(self, root_dir, name='csv', **kwargs):
        super().__init__(name)
        self._root = AsyncPath(root_dir)
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
            rows = key_group[key]
            filename = key
            await self._root.mkdir(parents=True, exist_ok=True)
            path = self._root / filename

            async with aiofiles.open(path, mode="a", encoding="utf-8", newline="") as afp:
                writer = AsyncWriter(afp, dialect="excel")
                await writer.writerows([[value for value in row.data.values()] for row in rows])

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
