from abc import ABC
from typing import List

from restweetution.models.storage.custom_data import CustomData


class Exporter(ABC):
    def __init__(self, name: str):
        self.name = name

    def save_custom_datas(self, datas: List[CustomData]):
        raise NotImplementedError('save_custom_datas')
