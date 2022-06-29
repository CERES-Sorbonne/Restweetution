import json
import os

from restweetution.collectors.async_client import AsyncClient
from restweetution.collectors.searcher import Searcher
from restweetution.storage.async_storage_manager import AsyncStorageManager
from restweetution.storage.object_storage.async_object_storage import AsyncFileStorage

if __name__ == "__main__":
    with open(os.getenv('CREDENTIALS'), 'r') as f:
        credentials = json.load(f)['token']
    s1 = AsyncFileStorage(root=os.getenv('ROOT_PATH'))
    m = AsyncStorageManager()
    m.add_storage(s1)
    c = AsyncClient(token=credentials)
    s = Searcher(client=c, storage_manager=m)