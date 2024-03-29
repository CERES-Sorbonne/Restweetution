import asyncio
import itertools
import math
from abc import ABC
from datetime import datetime
from typing import Callable, Dict

from pydantic import BaseModel

from restweetution.utils import Event


class TaskInfo(BaseModel):
    id: int
    name: str
    started_at: datetime
    is_running: bool
    progress: int
    max_progress: int
    result: Dict = {}
    key: str = None


class ServerTask(ABC):
    id_iter = itertools.count()

    def __init__(self, name: str):
        self.id = next(ServerTask.id_iter)
        self.name = name
        self.result = {}
        self.on_finish: Event = Event()
        self.task: asyncio.Task | None = None
        self.started_at: datetime | None = None
        self._progress: int = 0
        self._max_progress: int = 1

    def is_running(self):
        return self.task and not self.task.done()

    def start(self, on_finish: Callable = None):
        if self.is_running():
            raise ValueError('Tried to start an already running Task')
        self._progress = 0
        if on_finish:
            self.on_finish.add(on_finish)
        self.task = asyncio.create_task(self._task_wrapper())
        self.started_at = datetime.now()

        return self.task

    def stop(self):
        self.task.cancel()
        self.on_finish(self.id)

    def get_progress(self):
        if self._max_progress == 0:
            return 100
        if self._progress == 0:
            return 0
        return math.floor(self._progress / self._max_progress * 100)

    async def _task_wrapper(self):
        await self._task_routine()
        self.on_finish(self)

    async def _task_routine(self):
        raise NotImplementedError('function _task not implemented')

    def get_info(self):
        return TaskInfo(id=self.id, name=self.name, started_at=self.started_at, is_running=self.is_running(),
                        progress=self._progress, result=self.result, max_progress=self._max_progress)
