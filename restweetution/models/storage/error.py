import json
from typing import Optional, Any

from pydantic import BaseModel

from restweetution.errors import RESTweetutionError, ResponseParseError, StorageError, TwitterAPIError
from restweetution.utils import get_full_class_name


class ErrorModel(BaseModel):
    def __init__(self, **kwargs):
        # if RESTweetutionError as init
        error = kwargs.get('error')
        if error:
            if isinstance(error, ResponseParseError) or isinstance(error, StorageError) or \
                    isinstance(error, TwitterAPIError):
                data = json.dumps(error.__dict__.copy(), default=str)
                error_name = get_full_class_name(error)
                super().__init__(error_name=error_name, data=data, **kwargs)
        else:
            super().__init__(**kwargs)

    error_name: str
    traceback: str
    data: Optional[Any]
    id: Optional[str]
