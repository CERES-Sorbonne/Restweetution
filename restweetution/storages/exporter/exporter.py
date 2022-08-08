from abc import ABC
from typing import List

from restweetution.models.storage.custom_data import CustomData


class Exporter(ABC):
    def save_custom_datas(self, datas: List[CustomData]):
        raise NotImplementedError('save_custom_datas')
