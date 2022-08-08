import asyncio
import tempfile

from restweetution.models.twitter.tweet import Tweet
from restweetution.storages import FileStorage


async def launch():
    with tempfile.TemporaryDirectory() as tdir:
        s1 = FileStorage(root=tdir)
        await s1.save_tweets([Tweet(**{'id': 123, 'text': 'toto', 'author_id': 1234})])
        print("toto")


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(launch())
    loop.run_forever()
