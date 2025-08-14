"""
Storage/persistence asynchronous stores and gets files from object storage.

"""

import fnmatch
from pathlib import Path
from typing import (
    IO,
    Any,
    AsyncGenerator,
    AsyncIterator,
    Dict,
    Generic,
    List,
    Optional,
    Tuple,
    Type,
    Union,
)

import asyncio
import atexit
import weakref

from azure.identity.aio import DefaultAzureCredential
from azure.storage.blob.aio import BlobServiceClient
from azure.core.exceptions import ResourceExistsError

from hopeit.dataobjects import DataObject, dataclass, dataobject
from hopeit.dataobjects.payload import Payload

from .partition import get_file_partition_key, get_partition_key

SUFFIX = ".json"

__all__ = ["ObjectStorage", "ObjectStorageSettings", "ConnectionConfig"]


@dataobject
@dataclass
class ConnectionConfig:
    """
    Azure Blob Storage connection configuration.

    :field connection_string, Optional[str]: Azure Storage account connection string.
    :field use_identity, bool: Use Azure Identity (DefaultAzureCredential) if True.
    :field account_name, Optional[str]: Azure Storage **account name** required when `use_identity=True`.
    """

    connection_string: Optional[str] = None
    use_identity: bool = False
    account_name: Optional[str] = None


@dataobject
@dataclass
class ObjectStorageSettings:
    """
    Azure Blob Storage ObjectStorage settings.

    :field bucket, str: Azure Blob Storage container name.
    :field prefix, Optional[str]: Prefix for every element stored.
    :field partition_dateformat, Optional[str]: Partitioning format.
    :field connection_config, ConnectionConfig: Connection configuration.
    """

    bucket: str
    connection_config: ConnectionConfig
    prefix: Optional[str] = None
    partition_dateformat: Optional[str] = None


@dataobject
@dataclass
class ItemLocator:
    item_id: str
    partition_key: Optional[str] = None


class ObjectStorage(Generic[DataObject]):
    """
    Stores and retrieves dataobjects and files from Azure Blob Storage
    """

    _session: BlobServiceClient
    _credential: Optional[DefaultAzureCredential]
    _registry: "weakref.WeakSet[ObjectStorage]" = weakref.WeakSet()
    _atexit_registered: bool = False

    @classmethod
    def _register_instance(cls, inst: "ObjectStorage") -> None:
        cls._registry.add(inst)
        if not cls._atexit_registered:
            atexit.register(cls._atexit_close_all)
            cls._atexit_registered = True

    def __init__(
        self,
        bucket: str,
        prefix: Optional[str] = None,
        partition_dateformat: Optional[str] = None,
    ) -> None:
        """
        Initialize ObjectStorage with the bucket name and optional partition_dateformat

        :param bucket, str: The name of the Azure Blob Storage bucket to use for storage
        :param prefix, Optional[str]: Prefix to be used for every element (object or file) stored in the Azure Blob Storage bucket.
        :param partition_dateformat, Optional[str]: Optional format string for partitioning
            dates in the Azure Blob Storage bucket.
        """
        self.bucket: str = bucket
        self.prefix: Optional[str] = (prefix.rstrip("/") + "/") if prefix else None
        self.partition_dateformat: str = (partition_dateformat or "").strip("/")
        self._settings: ObjectStorageSettings
        self._conn_config: Dict[str, Any]
        self._session = None  # type: ignore[assignment]
        self._credential = None

    @classmethod
    def with_settings(
        cls, settings: Union[ObjectStorageSettings, Dict[str, Any]]
    ) -> "ObjectStorage":
        """
        Create an ObjectStorage instance with settings

        :param settings, `ObjectStorageSettings` or `Dict[str, Any]`:
            Either an :class:`ObjectStorageSettings` object or a dictionary
            representing ObjectStorageSettings.
        :return `ObjectStorage`
        """
        if settings and not isinstance(settings, ObjectStorageSettings):
            settings = Payload.from_obj(settings, ObjectStorageSettings)
        assert isinstance(settings, ObjectStorageSettings)
        obj = cls(
            bucket=settings.bucket,
            prefix=settings.prefix,
            partition_dateformat=settings.partition_dateformat,
        )
        obj._settings = settings
        return obj

    async def connect(
        self, *, connection_config: Union[ConnectionConfig, Dict[str, Any], None] = None
    ):
        """
        Creates an ObjectStorage connection pool for Azure Blob Storage.

        :param connection_config: `ConnectionConfig` or `Dict[str, Any]`
        """
        assert self.bucket

        if connection_config and not isinstance(connection_config, ConnectionConfig):
            connection_config = Payload.from_obj(connection_config, ConnectionConfig)

        self._conn_config = Payload.to_obj(  # type: ignore[assignment]
            connection_config if connection_config else self._settings.connection_config
        )

        conn_str = self._conn_config.get("connection_string")
        use_identity = self._conn_config.get("use_identity", False)

        if conn_str:
            self._session = BlobServiceClient.from_connection_string(conn_str)
            self._credential = None
        elif use_identity:
            account_name = self._conn_config.get("account_name")
            if not account_name:
                raise ValueError("ConnectionConfig.account_name is required when use_identity=True")
            self._credential = DefaultAzureCredential()
            account_url = f"https://{account_name}.blob.core.windows.net"
            self._session = BlobServiceClient(account_url=account_url, credential=self._credential)
        else:
            raise ValueError(
                "Either connection_string or use_identity must be provided in ConnectionConfig."
            )

        ObjectStorage._register_instance(self)
        return self

    @classmethod
    def _atexit_close_all(cls) -> None:
        async def _close_all():
            for inst in list(cls._registry):
                try:
                    await inst.aclose()
                except Exception:
                    # best-effort at shutdown
                    pass

        try:
            asyncio.run(_close_all())
        except RuntimeError:
            loop = asyncio.new_event_loop()
            try:
                loop.run_until_complete(_close_all())
            finally:
                loop.close()

    async def get(
        self,
        key: str,
        *,
        datatype: Type[DataObject],
        partition_key: Optional[str] = None,
    ):
        """
        Retrieves value under specified key, converted to datatype

        :param key, str
        :param datatype: dataclass implementing @dataobject (@see DataObject)
        :param partition_key, Optional[str]: Optional partition key
        :return: instance
        """
        blob_key = self._build_key(partition_key=partition_key, key=f"{key}{SUFFIX}")
        container_client = self._session.get_container_client(self.bucket)
        blob_client = container_client.get_blob_client(blob_key)
        try:
            stream = await blob_client.download_blob()
            data = await stream.readall()
            if data:
                return Payload.from_json(data, datatype)
            return None
        except Exception as e:
            # Optionally, check for specific Azure error codes for not found
            if hasattr(e, "status_code") and e.status_code == 404:
                return None
            return None  # or raise e for other errors

    async def get_file(
        self,
        file_name: str,
        *,
        partition_key: Optional[str] = None,
    ) -> Optional[bytes]:
        """
        Download a file from Azure Blob Storage and return its contents as bytes

        :param file_name, str: The name of the file to download
        :param partition_key, Optional[str]: Optional partition key
        :return: The contents of the requested file as bytes, or None if the file does not exist
        """
        blob_key = self._build_key(partition_key=partition_key, key=file_name)
        container_client = self._session.get_container_client(self.bucket)
        blob_client = container_client.get_blob_client(blob_key)
        try:
            stream = await blob_client.download_blob()
            data = await stream.readall()
            return data
        except Exception:
            # Optionally, handle not found or log error
            return None

    async def get_file_chunked(
        self,
        file_name: str,
        *,
        partition_key: Optional[str] = None,
    ) -> AsyncIterator[Tuple[Optional[bytes], int]]:
        """
        Download a blob from Azure Blob Storage in chunks.

        :param file_name str: object id
        :param partition_key, Optional[str]: Optional partition key.

        Yields:
            Tuple[Optional[bytes], int]: (chunk, total_content_length)
        """
        blob_key = self._build_key(partition_key=partition_key, key=file_name)
        container_client = self._session.get_container_client(self.bucket)
        blob_client = container_client.get_blob_client(blob_key)
        try:
            stream = await blob_client.download_blob()
            content_length = stream.size
            async for chunk in stream.chunks():
                yield chunk, content_length
        except Exception:
            # Optionally, handle not found or log error
            yield None, 0

    async def store(self, *, key: str, value: DataObject) -> str:
        """
        Upload a @dataobject object to Azure Blob Storage

        :param key: object id
        :param value: hopeit @dataobject
        """
        partition_key = None
        if self.partition_dateformat:
            partition_key = get_partition_key(value, self.partition_dateformat)

        blob_key = self._build_key(partition_key=partition_key, key=f"{key}{SUFFIX}")
        container_client = self._session.get_container_client(self.bucket)
        blob_client = container_client.get_blob_client(blob_key)

        data = Payload.to_json(value).encode()
        await blob_client.upload_blob(data, overwrite=True)
        return self._prune_prefix(blob_key)

    async def store_file(self, *, file_name: str, value: Union[bytes, IO[bytes], Any]) -> str:
        """
        Stores bytes or a file-like object in Azure Blob Storage.

        :param file_name, str
        :param value, Union[bytes, any]: bytes or a file-like object to store, it must
            implement the read method and must return bytes.
        :return, str: file location
        """
        partition_key = None
        if self.partition_dateformat:
            partition_key = get_file_partition_key(self.partition_dateformat)
        key = self._build_key(partition_key=partition_key, key=file_name)
        container_client = self._session.get_container_client(self.bucket)
        blob_client = container_client.get_blob_client(key)

        await blob_client.upload_blob(value, overwrite=True)
        return self._prune_prefix(key)

    async def list_objects(
        self, wildcard: str = "*", *, recursive: bool = False
    ) -> List[ItemLocator]:
        """
        Retrieves list of objects keys from the object storage

        :param wildcard: allow filter the listing of objects
        :return: List of `ItemLocator` with objects location info
        """
        wildcard = wildcard + SUFFIX
        n_part_comps = len(self.partition_dateformat.split("/"))
        item_list = []
        async for key in self._aioglob(wildcard, recursive):
            item_list.append(key)
        return [self._get_item_locator(item_path, n_part_comps, SUFFIX) for item_path in item_list]

    async def delete(self, *keys: str, partition_key: Optional[str] = None):
        """
        Delete specified keys

        :param keys: str, keys to be deleted
        :param partition_key, Optional[str]: Optional partition key
        """
        container_client = self._session.get_container_client(self.bucket)
        for key in keys:
            blob_key = self._build_key(partition_key=partition_key, key=f"{key}{SUFFIX}")
            blob_client = container_client.get_blob_client(blob_key)
            try:
                await blob_client.delete_blob()
            except Exception:
                # Optionally, handle not found or log error
                pass

    async def delete_files(self, *file_names: str, partition_key: Optional[str] = None):
        """
        Delete specified file_names

        :param file_names: str, file names to be deleted
        :param partition_key, Optional[str]: Optional partition key
        """
        container_client = self._session.get_container_client(self.bucket)
        for file_name in file_names:
            blob_key = self._build_key(partition_key=partition_key, key=file_name)
            blob_client = container_client.get_blob_client(blob_key)
            try:
                await blob_client.delete_blob()
            except Exception:
                # Optionally, handle not found or log error
                pass

    async def list_files(
        self, wildcard: str = "*", *, recursive: bool = False
    ) -> List[ItemLocator]:
        """
        Retrieves list of files_names from the object storage

        :param wildcard, str: allow filter the listing of objects
        :return: List of `ItemLocator` with file location info
        """
        n_part_comps = len(self.partition_dateformat.split("/"))
        item_list = []
        async for key in self._aioglob(wildcard, recursive):
            item_list.append(key)
        return [self._get_item_locator(item_path, n_part_comps) for item_path in item_list]

    def partition_key(self, path: str) -> str:
        """
        Get the partition key for a given path.

        :param path, str
        :return str: the extracted partition key.
        """
        partition_key = ""
        if self.partition_dateformat:
            partition_key = path.rsplit("/", 1)[0]
        return partition_key

    async def create_bucket(self, exist_ok: bool = False):
        """
        Creates a container in Azure Blob Storage if it doesn't already exist.

        :param exist_ok, bool: If False, raises an error if the container already exists (default is False).
        """
        container_client = self._session.get_container_client(self.bucket)
        try:
            await container_client.create_container()
        except ResourceExistsError as e:
            # If container exists and exist_ok is True, ignore error
            if exist_ok and hasattr(e, "error_code") and e.error_code == "ContainerAlreadyExists":
                return
            # For Azure, error_code may not always be present, so check message as fallback
            if exist_ok and "ContainerAlreadyExists" in str(e):
                return
            raise e

    async def _aioglob(
        self,
        wildcard: Optional[str] = None,
        recursive: bool = False,
    ) -> AsyncGenerator[str, None]:
        """
        A generator function similar to `glob` that lists files in an Azure Blob Storage container.

        :param wildcard, Optional[str]: Pattern to match file keys against.
        :param recursive, bool: If True, lists files recursively.

        :yields: str: The keys of the files that match the criteria.
        """
        # Use self._session (BlobServiceClient) and self.bucket (container name)
        container_client = self._session.get_container_client(self.bucket)
        prefix = self.prefix or ""

        # If wildcard is specified, try to optimize prefix
        if wildcard:
            dir_path = Path(wildcard).parent
            if dir_path != Path("."):
                prefix += f"{dir_path}/"

        # Azure does not support delimiter in list_blobs, so we filter manually
        async for blob in container_client.list_blobs(name_starts_with=prefix):
            key = blob.name
            # If not recursive, skip blobs not directly under prefix
            if not recursive and "/" in key[len(prefix) :]:
                continue
            # Wildcard filtering
            if wildcard and not fnmatch.fnmatch(
                key, self._build_key(partition_key=None, key=wildcard)
            ):
                continue
            yield self._prune_prefix(key)

    def _build_key(self, partition_key: Optional[str], key: str) -> str:
        """
        Build the key based on the prefix, partition key, and base key.

        :param partition_key: Optional[str]: The partition key to add to the key.
        :param key: str: The base file key.
        :return: The constructed file key.
        """
        return f"{self.prefix or ''}{partition_key.rstrip('/') + '/' if partition_key else ''}{key}"

    def _get_item_locator(
        self, item_path: str, n_part_comps: int, suffix: Optional[str] = None
    ) -> ItemLocator:
        """This method generates an `ItemLocator` object from a given `item_path`"""
        comps = item_path.split("/")

        if not self.partition_dateformat:
            return ItemLocator(item_id=item_path[: -len(suffix)] if suffix else item_path)
        partition_key = "/".join(comps[0:n_part_comps])

        item_id = (
            "/".join(comps[n_part_comps:])[: -len(suffix)]
            if suffix
            else "/".join(comps[n_part_comps:])
        )
        return ItemLocator(item_id=item_id, partition_key=partition_key)

    def _prune_prefix(self, file_path: str) -> str:
        if self.prefix:
            return file_path[len(self.prefix) :]
        return file_path

    async def aclose(self) -> None:
        """Close underlying async clients/credentials to avoid aiohttp session leaks."""
        # Close BlobServiceClient
        session = getattr(self, "_session", None)
        if session is not None:
            try:
                close = getattr(session, "close", None)
                if close is not None:
                    if asyncio.iscoroutinefunction(close):
                        await close()
                    else:
                        close()
            except Exception:
                pass
        # Close DefaultAzureCredential if present
        cred = getattr(self, "_credential", None)
        if cred is not None:
            try:
                aclose = getattr(cred, "aclose", None)
                if aclose is not None and asyncio.iscoroutinefunction(aclose):
                    await aclose()
                else:
                    close = getattr(cred, "close", None)
                    if close is not None:
                        if asyncio.iscoroutinefunction(close):
                            await close()
                        else:
                            close()
            except Exception:
                pass
