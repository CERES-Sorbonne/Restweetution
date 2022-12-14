import json
from typing import Protocol

from restweetution.models.twitter import Media


class Event(set):
    """
    """

    async def __call__(self, *args, **kwargs):
        for f in self:
            await f(*args, **kwargs)

    def __repr__(self):
        return "Event(%s)" % list.__repr__(self)


def get_full_class_name(obj):
    module = obj.__class__.__module__
    if module is None or module == str.__class__.__module__:
        return obj.__class__.__name__
    return module + '.' + obj.__class__.__name__


class DownloadCallback(Protocol):
    async def __call__(self, media: Media, sha1: str, bytes_image: bytes, media_format: str) -> None: ...


def clean_dict(data):
    keys = list(data.keys())
    for k in keys:
        if not data[k]:
            data.pop(k)
    return data


def safe_json(data):
    return json.dumps(data, default=str)


def safe_dict(data):
    return json.loads(safe_json(data))
