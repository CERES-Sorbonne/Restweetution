import json
import traceback
from typing import Optional, Any

from pydantic import BaseModel

from restweetution.errors import ResponseParseError, StorageError, TwitterAPIError
from restweetution.utils import get_full_class_name


class ErrorModel(BaseModel):
    def __init__(self, **kwargs):
        # if RESTweetutionError as init
        error = kwargs.get('error')
        if error:
            trace = traceback.format_exc()
            kwargs['traceback'] = trace
            if isinstance(error, ResponseParseError) or isinstance(error, StorageError) or \
                    isinstance(error, TwitterAPIError):
                data = error.__dict__.copy()
                error_name = get_full_class_name(error)
                super().__init__(error_name=error_name, data=data, **kwargs)
        else:
            super().__init__(**kwargs)

    error_name: str
    traceback: str
    data: Optional[Any]
    id: Optional[int]
