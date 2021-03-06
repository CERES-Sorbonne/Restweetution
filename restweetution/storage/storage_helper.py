import io
from abc import ABC
from typing import Union


class StorageHelper(ABC):
    """
    Metaclass to define some generic storage methods that will be implemented in every type of storage
    """
    def __init__(self, *args, **kwargs):
        self.root = None

    async def get(self, key: str) -> io.BufferedIOBase:
        """
        Return the specified object from the storage
        :param key: the key identifying the object
        :return: a buffer containing the storage
        """
        pass

    async def put(self, buffer: Union[io.BufferedIOBase, str], key: str) -> str:
        """
        Save to storage the object
        :param buffer: the buffer of the object to save, can be an io.BufferedIOBase kind or a string
        :param key: the key that will be used to retrieve the object later
        :return: absolute uri to the created resource
        """
        pass

    def delete(self, key: str) -> None:
        """
        Delete the specified object from the storage
        :param key: the key identifying the object
        :return: None
        """
        pass

    def list(self, prefix=None, recursive=False) -> [str]:
        """
        List all objects in the root directory
        :param prefix: used to filter the results (name, subdirectory) etc.
        for instance, storage.list(prefix="/tweet") will return all objects stored under the tweet repository
        :param recursive: if set to true, will recurse through all sub folders
        :return: a list of strings containing the keys of the objects
        """
        pass

    def exists(self, key: str) -> bool:
        """
        Return whether a key exists or not
        :param key: the key to check
        :return: a bool
        """

    def has_free_space(self) -> bool:
        """
        Is there still enough space in the storage to store tweet ?
        :return: a boolean
        """
        pass
