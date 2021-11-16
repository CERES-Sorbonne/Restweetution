import io
import os
from pathlib import Path
from typing import Union

from restweetution.storage.storage import Storage


class FileStorage(Storage):
    def __init__(self, root: str, max_size: int = None):
        super().__init__()
        self._root = root
        self.max_size = max_size
        # use this so we can override it in the ssh client
        self._open = open
        # same for join
        self._join_path = os.path.join

    @property
    def root(self):
        return self._root

    @root.setter
    def root(self, value):
        if value:
            self.safe_create(value)
        self._root = value

    def get(self, key: str) -> io.BufferedIOBase:
        with self._open(self._join_path(self.root, key), 'rb') as f:
            return io.BytesIO(f.read())

    def put(self, buffer: Union[io.BufferedIOBase, str], key: str) -> str:
        # create directory if it does not exist
        dir_name = os.path.dirname(key)
        self.safe_create(dir_name)
        path = self._join_path(self.root, key)
        if isinstance(buffer, str):
            with self._open(path, 'w', encoding='utf-8') as f:
                f.write(buffer)
        elif isinstance(buffer, io.BufferedIOBase):
            buffer.seek(0)
            with self._open(path, 'wb') as f:
                f.write(buffer.read())
        return path

    def delete(self, key: str):
        pass

    def list(self, prefix: str = None, recursive: bool = False):
        if not recursive:
            path = self._join_path(self.root, prefix or "")
            return os.listdir(path)
        else:
            raise NotImplemented("Recursive List not implemented yet")

    @property
    def has_free_space(self) -> bool:
        if self.max_size is None:
            return True
        if self._get_folder_size() < self.max_size * 1000000:
            return True
        return False

    def exists(self, key: str) -> bool:
        return os.path.exists(self._join_path(self.root, key))

    def _get_folder_size(self):
        """
        Utility function to find the size of a folder
        :return: in octets, the size of the current storage
        """
        return sum(f.stat().st_size for f in Path(self.root).glob('**/*') if f.is_file())

    def safe_create(self, dir_path):
        """
        Utility method to create a folder if it does not exist
        """
        directory = Path(self._join_path(self.root, dir_path))
        directory.mkdir(parents=True, exist_ok=True)
