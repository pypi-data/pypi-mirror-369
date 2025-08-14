# hopeit.azure.blob-storage plugin

This library is part of hopeit.engine:

> visit: https://github.com/hopeit-git/hopeit.engine

This library provides a `ObjectStorage` class to store and retrieve `@dataobjects` and files from Azure Blob Storage and compatible services as a plugin for the popular [`hopeit.engine`](https://github.com/hopeit-git/hopeit.engine) reactive microservices framework.

It supports the `prefix` setting, which is a prefix to be used for every element (object or file) stored in the Azure Blob Storage bucket. This prefix can be used to organize and categorize stored data within the bucket. Additionally, it supports the `partition_dateformat` setting, which is a date format string used to prefix file names for partitioning saved files into different subfolders based on the event timestamp (event_ts()). For example, using `%Y/%m/%d` will store each data object in a folder structure like year/month/day/, providing a way to efficiently organize and retrieve data based on date ranges. These settings can be used together to achieve more granular organization of data within the bucket.

### Installation

Python library that provides helpers to store and retrieve `@dataobjects` and files to Azure Blob Storage compatible services

```bash
pip install hopeit.azure.blob-storage
```

### Usage

```python
from hopeit.dataobjects import dataobject, dataclass
from hopeit.azure.blob_storage import ObjectStorage, ObjectStorageSettings, ConnectionConfig

# Set a connection configuration
conn_config = ConnectionConfig(
    connection_string="__AZURE_CONNECTION_STRING__",
    use_identity=False,
)

# Set settings for ObjectStorage
settings = ObjectStorageSettings(
    bucket="your-bucket-name",
    connection_config=conn_config
)

# Create an ObjectStorage instance
storage = await ObjectStorage.with_settings(settings).connect()

# hopeit.engine data object
@dataobject
@dataclass
class Something:
    key: str
    value: str

something = Something(key="my_key", value="some_value")

# Store a data object
await storage.store(key=something.key, value=something)

# Retrieve a data object
retrieved_object = await storage.get(key=something.key, datatype=Something)
print(retrieved_object)
```

## Example Usage

In the `apps/examples/azure-example/` directory, you can find a full example `hopeit.engine` app that demonstrates the usage of the `hopeit.azure.blob-storage` plugin within the `hopeit.engine` framework. This example showcases how to store and retrieve `@dataobjects` and files from Azure Blob Storage using the `ObjectStorage` class.
