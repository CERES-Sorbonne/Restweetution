import io
import os
from pathlib import Path
from typing import Union

from restweetution.models.config import FileStorageConfig, SSHFileStorageConfig
from restweetution.storage.storage import Storage
from smart_open import open


class FileStorage(Storage):
    def __init__(self, config: FileStorageConfig):
        super().__init__(config=config)
        self.safe_create(self._root_directory)

    @property
    def root_directory(self):
        return self._root_directory

    @root_directory.setter
    def root_directory(self, value):
        self.safe_create(value)
        self._root_directory = value

    def get(self, key: str) -> io.BufferedIOBase:
        with open(os.path.join(self.root_directory, key), 'rb') as f:
            return io.BytesIO(f.read())

    def put(self, buffer: Union[io.BufferedIOBase, str], key: str) -> str:
        # create directory if it does not exist
        dir_name = os.path.dirname(key)
        self.safe_create(os.path.join(self.root_directory, dir_name))
        path = os.path.join(self.root_directory, key)
        if isinstance(buffer, str):
            with open(path, 'w', encoding='utf-8') as f:
                f.write(buffer)
        elif isinstance(buffer, io.BufferedIOBase):
            buffer.seek(0)
            with open(path, 'wb') as f:
                f.write(buffer.read())
        return path

    def delete(self, key: str):
        pass

    def list(self, prefix: str = None, recursive: bool = False):
        if not recursive:
            path = os.path.join(self.root_directory, prefix or "")
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
        return os.path.exists(key)

    def _get_folder_size(self):
        """
        Utility function to find the size of a folder
        :return: in octets, the size of the current storage
        """
        return sum(f.stat().st_size for f in Path(self.root_directory).glob('**/*') if f.is_file())

    @staticmethod
    def safe_create(dir_path):
        """
        Utility method to create a folder if it does not exist
        """
        directory = Path(dir_path)
        directory.mkdir(parents=True, exist_ok=True)


class SSHFileStorage(FileStorage):
    def __init__(self, config: SSHFileStorageConfig):
        super().__init__(FileStorageConfig(root_directory=config.root_directory))
        self.root_directory = f"ssh://{config.user}:{config.password}@{config.host}/{config.root_directory}"
