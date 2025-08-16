import os
import uuid
from pathlib import Path

import boto3

from ..loggers.logger import Logger

logger = Logger()


class DeleteFailed(Exception):
    pass


class DownloadFailed(Exception):
    pass


class StorageConnectionFailed(Exception):
    pass


class UploadFailed(Exception):
    pass


class AbstractStorage:
    # internal use only
    _storage_client = None

    # extension required
    bucket_name = None
    bucket_public_url = None

    class File:
        def __init__(self, remote_path=None, local_path=None, url=None):
            self.remote_path = remote_path
            self.local_path = local_path
            self.url = url

    def __init__(self, *args, **kwargs):
        logger.debug(f"{self.__class__.__name__}.__init__", priority=2)

        # share the storage client at the global level
        if AbstractStorage._storage_client is None:
            try:
                logger.debug("connecting to s3", priority=3)
                logger.debug(f"bucket_name: {self.bucket_name}")
                AbstractStorage._storage_client = boto3.client("s3")
            except Exception as e:
                logger.error(f"{self.__class__.__name__}.__init__ - error", priority=3)
                logger.error(f"{e.__class__.__name__}: {str(e)}")
                raise StorageConnectionFailed(str(e))

    def upload(self, local_file_path, remote_file_path=None):
        if remote_file_path is None:
            remote_file_path = f"{uuid.uuid4()}-{os.path.basename(local_file_path)}"

        logger.debug(f"{self.__class__.__name__}.upload", priority=2)
        logger.debug(f"local_file_path: {local_file_path}")
        logger.debug(f"remote_file_path: {remote_file_path}")

        try:
            self._storage_client.upload_file(local_file_path, self.bucket_name, remote_file_path)
        except Exception as e:
            logger.error(f"{self.__class__.__name__}.upload - error", priority=3)
            logger.error(f"{e.__class__.__name__}: {str(e)}")
            raise UploadFailed(str(e))

        return self.File(
            remote_path=remote_file_path,
            local_path=local_file_path,
            url=f"{self.bucket_public_url}/{remote_file_path}",
        )

    def download(self, remote_file_path, local_file_path=None):
        if local_file_path is None:
            local_file_path = os.path.join(os.getcwd(), remote_file_path)

        # ensure local_file_path directories exist
        Path(os.path.dirname(local_file_path)).mkdir(parents=True, exist_ok=True)

        logger.debug(f"{self.__class__.__name__}.download", priority=2)
        logger.debug(f"remote_file_path: {remote_file_path}")
        logger.debug(f"local_file_path: {local_file_path}")

        try:
            self._storage_client.download_file(self.bucket_name, remote_file_path, local_file_path)
        except Exception as e:
            logger.error(f"{self.__class__.__name__}.download - error", priority=3)
            logger.error(f"{e.__class__.__name__}: {str(e)}")
            raise DownloadFailed(str(e))

        return self.File(
            remote_path=remote_file_path,
            local_path=local_file_path,
            url=f"{self.bucket_public_url}/{remote_file_path}",
        )

    def delete(self, remote_file_path):
        logger.debug(f"{self.__class__.__name__}.delete", priority=2)
        logger.debug(f"remote_file_path: {remote_file_path}")

        try:
            self._storage_client.delete_object(Bucket=self.bucket_name, Key=remote_file_path)
        except Exception as e:
            logger.error(f"{self.__class__.__name__}.delete - error", priority=3)
            logger.error(f"{e.__class__.__name__}: {str(e)}")
            raise DeleteFailed(str(e))

        return True
