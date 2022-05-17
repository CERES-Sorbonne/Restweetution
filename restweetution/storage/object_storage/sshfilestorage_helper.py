import os

import pysftp

from .filestorage_helper import FileStorageHelper


class SSHFileStorageHelper(FileStorageHelper):
    def __init__(self, root: str, max_size: int = None, *, host: str, user: str, password: str = ""):
        super().__init__(root, max_size)
        self._sftp = pysftp.Connection(host, username=user, password=password)
        try:
            self._sftp.chdir(root)
        except FileNotFoundError:
            raise FileNotFoundError(f"It seems that the path {root} does not exist on the remote machine")
        self._join_path = lambda *args: os.path.normpath(os.path.join(*args)).replace('\\', '/')
        # do this because sftp open does not support more than the name of the file and the mode (e.g encoding not supported)
        self._open = lambda *args, **kwargs: self._sftp.open(args[0], args[1])

    def list(self, prefix: str = "", recursive: bool = False):
        if not recursive:
            return self._sftp.listdir(prefix)
        else:
            raise NotImplemented("Recursive List not implemented yet")

    def safe_create(self, dir_path):
        """
        Utility method to create a folder if it does not exist
        """
        self._sftp.makedirs(dir_path)

    def exists(self, key: str) -> bool:
        return self._sftp.exists(key)

    @property
    def has_free_space(self) -> bool:
        if self.max_size is None:
            return True
        if self._get_folder_size() < self.max_size * 1000000:
            return True
        return False

    def _get_folder_size(self):
        """
        Utility function to find the size of a folder
        :return: in octets, the size of the current storage
        """
        return sum([f.st_size for f in self._sftp.listdir_attr()])
