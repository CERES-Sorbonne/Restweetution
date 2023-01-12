from abc import ABC
from typing import List

from aiopath import AsyncPath

from restweetution.models.storage.custom_data import CustomData


class Exporter(ABC):
    def __init__(self, name: str):
        self.name = name

    async def save_custom_datas(self, datas: List[CustomData]):
        raise NotImplementedError('save_custom_datas')


class FileExporter(Exporter, ABC):
    def get_root(self) -> AsyncPath:
        raise NotImplementedError('get_root is not implemented')
