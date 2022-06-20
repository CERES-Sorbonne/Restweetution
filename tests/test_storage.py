import io
import json
import os

import pytest
from PIL import Image

from restweetution.models.stream_config import FileStorageConfig
from restweetution.storage.object_storage.filestorage_helper import FileStorageHelper


class StorageProvider:
    def __init__(self, storage):
        self.storage = storage

    def create_objects(self, key_list=[]):
        for key in key_list:
            self.storage.put(json.dumps({'foo': 'bar'}), key=f"{key}")


@pytest.fixture(params=["FS"])
def storage(request, tmp_path):
    if request.param == "FS":
        return FileStorageHelper(FileStorageConfig(root_directory=tmp_path))


@pytest.fixture
def storage_provider(storage):
    return StorageProvider(storage)


@pytest.fixture
def key_list():
    return ['test.json', 'tweet.json', 'test/test2.json', 'test/test1/test3.json']


@pytest.fixture
def storage_provider_with_list(storage_provider, key_list):
    storage_provider.create_objects(key_list)
    return storage_provider


def test_put_json(storage):
    buffer = io.BytesIO()
    json.dump({"foo": "bar"}, buffer)
    storage.put(buffer, key="foo.json")


def test_put_image(storage):
    with open(os.path.join(os.path.dirname(__file__), 'resources', 'img.png'), 'rb') as f:
        storage.put(io.BytesIO(f.read()), key="img.png")


def test_get_json(storage_provider):
    storage_provider.create_objects(['test.json'])
    res = storage_provider.storage.get('test.json')
    json.load(res)


def test_get_image(storage):
    with open(os.path.join(os.path.dirname(__file__), 'resources', 'img.png'), 'rb') as f:
        storage.put(io.BytesIO(f.read()), key="img.png")
    Image.open(storage.get('img.png'))


def test_get_non_existent_file(storage):
    with pytest.raises(FileNotFoundError):
        storage.get('nonexistent.file')


def test_list(storage_provider_with_list):
    assert storage_provider_with_list.storage.list() == ['test.json', 'tweet.json', 'test']


def test_list_prefix(storage_provider_with_list):
    assert storage_provider_with_list.storage.list(prefix='test') == ['test/test2.json', 'test/test1']


def test_list_recursive(storage_provider_with_list, key_list):
    assert storage_provider_with_list.storage.list(recursive=True) == key_list


def test_list_prefix_recursive(storage_provider_with_list, key_list):
    assert storage_provider_with_list.storage.list(recursive=True, prefix='test') == ['test/test2.json', 'test/test1/test3.json']


def test_delete(storage_provider):
    storage_provider.create_objects(["foo.json"])
    storage_provider.storage.delete('foo.json')
    assert storage_provider.storage.list() == []
