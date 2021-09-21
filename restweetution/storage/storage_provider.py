from restweetution.models.config import StorageConfig, FileStorageConfig, SSHFileStorageConfig
from restweetution.storage.filestorage import FileStorage, SSHFileStorage


def storage_provider(config: StorageConfig):
    if isinstance(config, FileStorageConfig):
        return FileStorage(config)
    elif isinstance(config, SSHFileStorageConfig):
        return SSHFileStorage(config)
    else:
        raise ValueError(f"Unhandled type of storage: {type(config)}")

