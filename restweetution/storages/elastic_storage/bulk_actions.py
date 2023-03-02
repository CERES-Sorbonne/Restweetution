from typing import List


class SaveAction(dict):
    def __init__(self, index, id_, doc):
        super().__init__()
        self['_op_type'] = 'index'
        self['_index'] = index
        self['_id'] = id_
        self['_source'] = doc


class UpdateAction(dict):
    def __init__(self, index, id_, doc, delete: List[str] = None):
        super().__init__()
        if delete is None:
            delete = []

        doc = {key: doc[key] for key in doc if doc[key] is not None or key in delete}

        self['_op_type'] = 'update'
        self['_index'] = index
        self['_id'] = id_
        self['doc'] = doc
