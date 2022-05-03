import asyncio
import time
from queue import Queue, Full
from threading import Thread


class CustomQueue:
    def __init__(self, maxsize=10, callback=None):
        self.q = Queue(maxsize=maxsize)
        self.callback = callback

    def set_callback(self, callback):
        self.callback = callback

    async def put(self, item):
        try:
            self.q.put_nowait(item)
        except Full:
            print("full!")
            await self.callback()
            self.q.put_nowait(item)

    def get(self):
        return self.q.get_nowait()

    def empty(self):
        return self.q.empty()

    def qsize(self):
        return self.q.qsize()


class StorageManager:
    def __init__(self, queue: CustomQueue):
        self.queue = queue

    async def check_queue(self, every=20):
        while True:
            if not self.queue.empty():
                await self.store_all()
            else:
                print("empty queue")
            await asyncio.sleep(every)

    async def store_all(self):
        print("clearing queue")
        while not self.queue.empty():
            self.store(self.queue.get())

    def store(self, item):
        print(item)


if __name__ == "__main__":
    # add continuously tasks to a queue
    # the storage then need to process them all N seconds
    q = CustomQueue(maxsize=5)
    s = StorageManager(q)
    q.set_callback(s.store_all)

    async def main():
        i = 0
        while True:
            await q.put("item" + str(i))
            print("adding new item")
            print(q.qsize())
            time.sleep(10)
            i += 1

    loop = asyncio.get_event_loop()
    loop.create_task(s.check_queue(20))
    loop.create_task(main())
    loop.run_forever()


