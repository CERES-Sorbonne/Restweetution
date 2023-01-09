import asyncio
import dataclasses
import time

from pydantic import BaseModel


class Model(BaseModel):
    a: str
    b: int
    c: bool

@dataclasses.dataclass
class Data:
    a: str
    b: int
    c: bool

async def main():
    dicts = [dict(a='non', b=1, c=True) for i in range(1000)]

    old = time.time()
    r1 = [Model(**d) for d in dicts]
    print(time.time() - old, ' s for BaseModel conversion')

    old = time.time()
    r2 = [Data(**d) for d in dicts]
    print(time.time() - old, ' s for Dataclass conversion')


asyncio.run(main())
