from collections.abc import Sequence
from datetime import datetime

from sqlalchemy import inspect
from sqlalchemy.orm import declarative_base


class CustomBase(object):
    def update(self, data: dict):
        for key, value in data.items():
            if self._is_basic_value(value) or self._is_basic_array(value):
                if hasattr(self, key):
                    setattr(self, key, value)

    def to_dict(self):
        ignore = inspect(self).unloaded
        data = {c.key: getattr(self, c.key)
                for c in inspect(self).mapper.column_attrs
                if c.key[0] != '_' and c.key not in ignore}

        for k, v in inspect(self).mapper.relationships.items():
            if k == '_parent' or k in ignore:
                continue
            items = getattr(self, k)
            if isinstance(items, Sequence):
                data[k] = [i.to_dict() for i in items]
            elif items:
                data[k] = items.to_dict()
        # remove None values from data
        for k in data.copy():
            if data[k] is None:
                data.pop(k)
        return data

    @staticmethod
    def _is_empty_dict(data: any):
        if isinstance(data, dict):
            for key in data:
                if data[key]:
                    return False
            return True
        return False

    @staticmethod
    def _is_basic_array(value):
        if isinstance(value, list):
            if len(value) > 0:
                return CustomBase._is_basic_value(value[0])
        return False

    @staticmethod
    def _is_basic_value(value):
        return isinstance(value, (str, int, float, bool, datetime))

    @staticmethod
    def _parse_key(key: str, data):
        key_list = key.split('.')
        nested_data = CustomBase._get_nested_value(key_list, data)
        db_key = '_'.join(key_list)
        return db_key, nested_data

    @staticmethod
    def _get_nested_value(key_list, data):
        value = data

        for key in key_list:
            if not value:
                return None
            if key in value:
                value = value[key]
            else:
                return None
        return value

    @staticmethod
    def prefix_to_dict(data: dict, prefix: str):
        keys = list(data.keys())
        p_len = len(prefix) + 1  # prefix length + 1 for the underscore
        keys_with_prefix = [k for k in keys if k.startswith(prefix + '_')]

        if keys_with_prefix:
            dico = {}
            for k in keys_with_prefix:
                new_key = k[p_len:]  # key without prefix
                dico[new_key] = data[k]
                data.pop(k)
            data[prefix] = dico

    def update_one_to_one(self, key, sqa_model, data):
        self.update_many_to_one(key, sqa_model, data)

    def update_many_to_one(self, key, sqa_model, data):
        db_key, nested_data = self._parse_key(key, data)
        if not nested_data:
            return
        if self._is_empty_dict(nested_data):
            return

        # print(args)
        sqa_model_object = sqa_model()
        sqa_model_object.update(nested_data)
        setattr(self, db_key, sqa_model_object)

    def update_one_to_many(self, key, sqa_model, data):
        db_key, nested_data = self._parse_key(key, data)
        if not nested_data:
            return
        if self._is_empty_dict(nested_data):
            return

        setattr(self, db_key, [])
        attr = getattr(self, db_key)

        for args in nested_data:
            sqa_model_object = sqa_model()
            sqa_model_object.update(args)
            attr.append(sqa_model_object)

    def update_value(self, key: str, data):
        keys = key.split('.')
        end_data = data
        for k in keys:
            if k not in end_data:
                return
            if end_data[k] is None:
                return
            end_data = end_data[k]

        setattr(self, '_'.join(keys), end_data)


Base = declarative_base(cls=CustomBase)
