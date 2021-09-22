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

    def get(self, key: str) -> io.BufferedIOBase:
        with open(os.path.join(self.root_directory, key), 'rb') as f:
            return io.BytesIO(f.read())

    def put(self, buffer: Union[io.BufferedIOBase, str], key: str):
        # create directory if it does not exist
        dir_name = os.path.dirname(key)
        directory = Path(os.path.join(self.root_directory, dir_name))
        directory.mkdir(parents=True, exist_ok=True)

        if isinstance(buffer, str):
            with open(os.path.join(self.root_directory, key), 'w', encoding='utf-8') as f:
                f.write(buffer)
        elif isinstance(buffer, io.BufferedIOBase):
            buffer.seek(0)
            with open(os.path.join(self.root_directory, key), 'wb', encoding='utf-8') as f:
                f.write(buffer.read())

    def delete(self, key: str):
        pass

    def list(self, prefix=None, recursive=False):
        pass

    def has_free_space(self) -> bool:
        if self.max_size is None:
            return True
        if self._get_folder_size() < self.max_size * 1000000:
            return True
        raise OSError("The maxsize of the storage directory has been reached")

    def _get_folder_size(self):
        """
        Utility function to find the size of a folder
        :return: in octets, the size of the current storage
        """
        return sum(f.stat().st_size for f in Path(self.root_directory).glob('**/*') if f.is_file())


class SSHFileStorage(FileStorage):
    def __init__(self, config: SSHFileStorageConfig):
        super().__init__(FileStorageConfig(root_directory=config.root_directory))
        self.root_directory = f"ssh://{config.user}:{config.password}@{config.host}/{config.root_directory}"
