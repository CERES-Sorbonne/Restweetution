import json
import os

from restweetution.twitter_client import TwitterClient
from restweetution.collectors.searcher import Searcher
from restweetution.storage.storage_manager import StorageManager
from restweetution.storage.object_storage.async_object_storage import AsyncFileStorage

if __name__ == "__main__":
    with open(os.getenv('CREDENTIALS'), 'r') as f:
        credentials = json.load(f)['token']
    s1 = AsyncFileStorage(root=os.getenv('ROOT_PATH'))
    m = StorageManager()
    m.add_storage(s1)
    c = TwitterClient(token=credentials)
    s = Searcher(client=c, storage_manager=m)