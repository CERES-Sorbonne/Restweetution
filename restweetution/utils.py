import asyncio
import json
from typing import Dict, List


class AsyncEvent(set):
    """
    Event utility class
    Can be used as set to add callbacks
    ex: event.add(callback)
    Use like a function et execute
    ex: event(*args, **kwargs)
    """
    tasks: List[asyncio.Task] = []

    async def __call__(self, *args, **kwargs):
        for f in self:
            await f(*args, **kwargs)

    def __repr__(self):
        return "AsyncEvent(%s)" % list.__repr__(self)


class Event(set):
    """
    Event utility class
    Can be used as set to add callbacks
    ex: event.add(callback)
    Use like a function et execute
    ex: event(*args, **kwargs)
    """

    def __call__(self, *args, **kwargs):
        for f in self:
            f(*args, **kwargs)

    def __repr__(self):
        return "Event(%s)" % list.__repr__(self)


global_task_list = []


def fire_and_forget(coro):
    task = asyncio.create_task(coro)
    global_task_list.append(task)
    task.add_done_callback(global_task_list.remove)
    return task


def get_full_class_name(obj):
    module = obj.__class__.__module__
    if module is None or module == str.__class__.__module__:
        return obj.__class__.__name__
    return module + '.' + obj.__class__.__name__


def clean_dict(data):
    """
    Removes Keys from dictionary if corresponding value is considered null
    @param data: Dictionary to be cleaned
    @return: Clean dictionary
    """
    keys = list(data.keys())
    for k in keys:
        if not data[k]:
            data.pop(k)
    return data


def safe_json(data: Dict):
    """
    safely convert a Dictionary to json data
    @param data: Dictionary
    @return: JSON string
    """
    return json.dumps(data, default=str)


def safe_dict(data):
    """
    Makes a dictionary safe for serialization
    @param data: Dictionary
    @return: Dictionary
    """
    return json.loads(safe_json(data))


def chunks(arr, n):
    for i in range(0, len(arr), n):
        yield arr[i:i + n]
