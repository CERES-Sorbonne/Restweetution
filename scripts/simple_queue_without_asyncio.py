import threading
import time
from queue import Queue, Full


class CustomQueue:
    def __init__(self, maxsize=10, callback=None):
        self.q = Queue(maxsize=maxsize)
        self.callback = callback

    def set_callback(self, callback):
        self.callback = callback

    def put(self, item):
        try:
            self.q.put_nowait(item)
        except Full:
            print("full!")
            self.callback()
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

    def check_queue(self, every=20):
        while True:
            if not self.queue.empty():
                self.store_all()
            else:
                print("empty queue")
            time.sleep(every)

    def store_all(self):
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

    def main():
        i = 0
        while True:
            q.put("item" + str(i))
            print("adding new item")
            print(q.qsize())
            time.sleep(1)
            i += 1

    t1 = threading.Thread(target=s.check_queue, args=[20])
    t2 = threading.Thread(target=main)
    t1.start()
    t2.start()
