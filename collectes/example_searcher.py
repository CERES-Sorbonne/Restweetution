import json
import os

from restweetution.twitter_client import TwitterClient
from restweetution.collectors.searcher import Searcher
from restweetution.storage_manager import StorageManager
from restweetution.storages import FileStorage

if __name__ == "__main__":
    with open(os.getenv('CREDENTIALS'), 'r') as f:
        credentials = json.load(f)['token']
    s1 = FileStorage(root=os.getenv('ROOT_PATH'))
    m = StorageManager()
    m.add_storage(s1)
    c = TwitterClient(token=credentials)
    s = Searcher(client=c, storage_manager=m)