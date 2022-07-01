import asyncio
import tempfile

from restweetution.models.twitter.tweet import RestTweet, Tweet
from restweetution.storage.object_storage.async_object_storage import AsyncFileStorage


async def launch():
    with tempfile.TemporaryDirectory() as tdir:
        s1 = AsyncFileStorage(root=tdir)
        await s1.save_tweets([RestTweet(**{'id': 123, 'text': 'toto', 'author_id': 1234})])
        print("toto")


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(launch())
    loop.run_forever()
