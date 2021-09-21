import io
from abc import ABC
from typing import Union

from restweetution.models.config import StorageConfig


class Storage(ABC):
    """
    Meta class to define some generic storage methods that will be implemented in every type of storage
    """
    def __init__(self, config: StorageConfig, *args, **kwargs):
        self.root_directory = config.root_directory
        self.max_size = config.max_size
        
    def get(self, key: str) -> io.BufferedIOBase:
        """
        Return the specified object from the storage
        :param key: the key identifying the object
        :return: a buffer containing the storage
        """
        pass

    def put(self, buffer: Union[io.BufferedIOBase, str], key: str) -> None:
        """
        Save to storage the object
        :param buffer: the buffer of the object to save, can be an io.BufferedIOBase kind or a string
        :param key: the key that will be used to retrieve the object later
        :return: None
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
        for instance, storage.list(prefix="/data") will return all objects stored under the data repository
        :param recursive: if set to true, will recurse trough all subfolders
        :return: a list of strings containing the keys of the objects
        """
        pass

    def has_free_space(self) -> bool:
        """
        Is there still enough space in the storage to store data ?
        :return: a boolean
        """
        pass
