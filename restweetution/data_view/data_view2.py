from abc import ABC
from typing import List, Dict, Any

from pydantic import BaseModel

from restweetution.collection import CollectionTree


def get_safe_set(data: Dict, fields: List[str]):
    def safe_set(field: str, value: Any):
        if not fields or field in fields:
            data[field] = value

    return safe_set


def get_any_field(fields: List[str]):
    def any_field(*field_list):
        if not fields:
            return True
        return any(f in fields for f in field_list)

    return any_field


class ViewDict(Dict):
    def __init__(self, id_: int | str, **kwargs):
        super().__init__(**kwargs)
        self['__id__'] = id_


class ViewResult(BaseModel):
    view: List[ViewDict]
    fields: List[str]
    default_fields: List[str]


class DataView2(ABC):
    @classmethod
    def compute(cls, tree: CollectionTree, ids: List[str | int] = None, fields: List[str] = None, all_fields=False,
                **kwargs) -> ViewResult:
        if not fields:
            fields = cls.get_default_fields() if not all_fields else cls.get_fields()

        view = cls._compute(tree=tree, ids=ids, fields=fields, **kwargs)
        return ViewResult(view=view, fields=cls.get_fields(), default_fields=cls.get_default_fields())

    @classmethod
    def _compute(cls, tree: CollectionTree, fields: List[str], ids: List[str | int] = None, **kwargs) -> List[ViewDict]:
        raise NotImplementedError('compute not implemented')

    @staticmethod
    def get_fields() -> List[str]:
        """
        Get all available fields for the view
        @return:
        """
        raise NotImplementedError('get_fields not implemented')

    @staticmethod
    def get_default_fields() -> List[str]:
        """
        Get some fields considered as interesting by default. Makes it easier to chose what to show in applications
        @return:
        """
        raise NotImplementedError('get_default_fields not implemented')
