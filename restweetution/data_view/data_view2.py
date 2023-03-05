from abc import ABC
from typing import List, Dict, Any, Callable

from pydantic import BaseModel


def get_safe_set(data: Dict, fields: List[str]):
    def safe_set(field: str, value: Any):
        if not fields or field in fields:
            data[field] = value

    return safe_set


def get_deep_set(safe_set: Callable, deep: bool):
    def deep_set(field: str, value: Any):
        if not deep:
            return
        safe_set(field, value)
    return deep_set


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

    @classmethod
    def all_if_empty(cls, fields: List[str]):
        if not fields:
            return cls.get_fields()
        return fields

    @classmethod
    def _result(cls, view_list: List[ViewDict], fields):
        return ViewResult(view=view_list, fields=fields, default_fields=cls.get_default_fields())
