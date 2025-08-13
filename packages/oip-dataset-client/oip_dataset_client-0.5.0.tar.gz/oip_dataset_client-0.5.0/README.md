# Dataset API Client

Welcome to __Open Innovation Dataset API Client__!  your gateway to seamless and efficient dataset management. Whether you're a data scientist, machine learning engineer, or anyone working with data, our dataset client empowers you to explore, interact, and manage datasets effortlessly. This guide provides an overview of the Dataset API client library, its installation, usage, and available methods.
To get started, install the library using pip. Once the library is installed, you can initialize the API client by providing the API server's hostname and an access token.


## Getting Started

The Open Innovation Dataset Client provides a convenient setup process to help you configure and initialize the client for interaction with the Open Innovation MLOps Platform. This setup involves setting up an environment variables that includes Open Innovation Platform (OIP) credentials and, optionally, storage provider credentials for services like AWS, Azure, GCP, or Minio.
Once the setup is complete, the Open Innovation Dataset Client is ready to use.
### Prerequisites

Before you begin, ensure that you have the following:

- Python is installed on your machine.
- Access to the Open Innovation web application to retrieve your OIP credentials.


### Setup Process

1. **Installation**

    Install the Open Innovation Dataset Client library using pip:

    ```
    pip install oip-dataset-client
    ```

2. **Initialization**

    The OIP Dataset Client provides multiple ways to get started. You can seamlessly initialize the client either by using our Python SDK or through a user-friendly command-line interface.
    

    1. **Python SDK** 

        To set up the Dataset API Client via Python SDK, you'll need to connect to the Dataset Server:
        
        

            from oip_dataset_client.dataset import DatasetClient
            
            api_host = "http://192.168.1.35:8000" # host of the server
            api_key = "72e3f81c-8c75-4f88-9358-d36a3a50ef36" # api-key of the user
            workspace_name = "default_workspace" # workspace name
            
            DatasetClient.connect(api_host=api_host, api_key=api_key, workspace_name=workspace_name)

        
        
        **Parameters**
        
        - `api_host` (str, required): The hostname of the Dataset API server.
        - `access_token` (str, required): Your API authentication token.
        - `workspace_name` (str, required): Your workspace name.
        - `verbose` (bool, optional): If True, enable console output for progress information by default it relies on `DatasetClient.verbose`(enabled by defaults) you can disable it by changing the value of DatasetClient.verbose  (`DatasetClient.verbose = False`).
        
        You can access both the Dataset API Server and your access token by requesting them through our MLOps Web UI.
        
    2. **Command-Line Interface** 

        If you prefer a more interactive setup, our CLI makes it easy to initialize the dataset client. Simply After installing the client, run the initialization command, and follow the prompts to configure your OIP credentials.
        
        - Run the following command to start the setup process:

            ```
            oip-dataset-client-init
            ```

        - Follow the instructions to input your OIP credentials.
        
## DatasetClient Methods
The DatasetClient class serves as the central component of the  oip_dataset_client. It acts as the core interface through which the client interacts with and manages datasets throughout their lifecycle, including creating, adding files, uploading, downloading, and finalizing.
The upcoming section will thoroughly cover the essential methods in this class.
### create

Create new datasets, these datasets serve as organized collections of data files, you have the flexibility to specify one or multiple parent datasets, allowing the newly created dataset to inherit all the files associated with its parent(s). Additionally, you can define the version for your dataset. This versioning feature enhances traceability and the ability to manage different iterations of your datasets. Furthermore, You can specify whether this dataset serves as the primary version among others and apply descriptive tags to categorize and detail the dataset's content. 

```python
my_dataset = DatasetClient.create(
    name="my_dataset",
    parent_datasets=[
        "8fb30519-8326-4f38-aa53-83ef35b65e6a",
        "a2c0c7b1-bb5f-49a1-8a47-2e1679a726bb",
    ],
    version="2.0.1",
    is_main=True
    tags=["testing","CSV","NASA"]
    description="a CSV testing dataset from NASA"
)
```
**Parameters**

- `name` (str, required): Name of the new dataset.
- `parent_datasets` (list[str], optional):  A list of parent datasets to extend the new dataset 
by adding all the files from their respective parent datasets.
- `version` (str, optional): Version of the new dataset, if no version is specified during creation, the default version will be set to 1.0.0  for the dataset's First version. For the next versions, we will automatically increment the highest semantic version available.
- `is_main` (bool, optional): True if the new dataset is the main version.
- `tags` (list[str], optional): Descriptive tags categorize datasets by keywords, detailing their subject matter, domain, or specific topics for better identification and organization.
- `description` (str, optional): A brief description of the new dataset.
- `verbose` (bool, optional): If True, enable console output for progress information by default it relies on `DatasetClient.verbose`(enabled by defaults) you can disable it by changing the value of DatasetClient.verbose  (`DatasetClient.verbose = False`).

**Returns**

- `Dataset`: Newly created Dataset object.

**Raises**

- `ValueError`: If the `name` is empty or `None`.
- `ValueError`: If any of the `parent_datasets` is not completed.


### add_files
You can add one or multiple files to the newly created dataset. When adding files, a thorough check is performed to ensure data integrity. The system checks if the files already exist in the dataset. If the file has already been uploaded or if it exists within one of the dataset's parent. However, if the file is not present or exists with different content, it is promptly added. In cases where files are found to be identical, they are simply ignored. This streamlined process ensures efficient management of your dataset's contents.

```python
my_dataset.add_files(path="absolute_path_to_the_files")
```

**Parameters**

- `path` (str, required): Path to the files we want to add to our dataset.
- `wildcard` (Union[str, List[str]], optional): Add a selective set of files by using wildcard matching, which can be a single string or a list of wildcard patterns.
- `recursive` (bool, optional): If True, match all wildcard files recursively.  Defaults to True.
- `max_workers` (int, optional): The number of threads to add the files with. Defaults to the number of logical cores.
- `verbose` (bool, optional): If True, enable console output for progress information by default it relies on `DatasetClient.verbose`(enabled by defaults) you can disable it by changing the value of DatasetClient.verbose  (`DatasetClient.verbose = False`).

**Returns**

- `int`: The number of files that have been added.
- `int`: The number of files that have been modified.

**Raises**

- `Exception`: If the dataset is in a final state, which includes `completed`, `aborted`, or `failed`.
- `ValueError`: If the specified path to the files does not exist.

### remove_files

You have the flexibility to remove one or multiple files from the dataset. 
This feature is particularly valuable when you need to eliminate specific files from the parent datasets.

```python
my_dataset.remove_files(path="relative_path_to_the_files")
```
**Parameters**

- `wildcard_path` (str, required): Wildcard path to the files to remove.
The path is always relative to the dataset (e.g. `folder/file*`).
- `recursive` (bool, optional): If True, match all wildcard files recursively. Defaults to True.
- `verbose` (bool, optional): If True, enable console output for progress information by default it relies on `DatasetClient.verbose`(enabled by defaults) you can disable it by changing the value of DatasetClient.verbose  (`DatasetClient.verbose = False`).

**Returns**

- `int`: The number of files that have been removed.

**Raises**

- `Exception`: If the dataset is in a final state, which includes `completed`, `aborted`, or `failed`.

### upload
After adding or removing files, you can proceed to the upload step, where you upload all the files to a storage provider. 
It's important to note that only files that haven't been uploaded yet are included in this process. 
In other words, this operation covers the direct files of the dataset, excluding the parent files, as those are already uploaded.

```python
my_dataset.upload()
```
**Parameters**

- `verbose` (bool, optional): If True, enable console output for progress information by default it relies on `DatasetClient.verbose`(enabled by defaults) you can disable it by changing the value of DatasetClient.verbose  (`DatasetClient.verbose = False`).

**Returns**

- `none`: Does not return any results.


**Raises**

- `Exception`: If the dataset is in a final state, which includes `completed`, `aborted`, or `failed`.
- `Exception`: If the upload failed. 

### finalize

Once all the files in the dataset have been successfully uploaded, you can proceed to finalize the dataset. 
It's important to note that once a dataset is finalized, no further operations can be performed on it.


```python
# if the files are not uploaded yet
# we can use the auto_upload=true ie my_dataset.finalize(auto_upload=true)
my_dataset.finalize()
```

**Parameters**

- `auto_upload` (bool, optional): Automatically upload dataset if not uploaded yet. Defaults to False.
- `verbose` (bool, optional): If True, enable console output for progress information by default it relies on `DatasetClient.verbose`(enabled by defaults) you can disable it by changing the value of DatasetClient.verbose  (`DatasetClient.verbose = False`).

**Returns**

- `none`: Does not return any results.


**Raises**

- `Exception`: If there is a pending upload.
- `Exception`: If the dataset's status is not valid for finalization. 

### get
Get a specific Dataset. If multiple datasets are found, the dataset with the highest semantic version is returned.
```python
my_dataset = DatasetClient.get(dataset_name="my_dataset")
```

**Parameters**

- `dataset_id` (str, optional): Requested dataset ID.
- `dataset_name` (str, optional): Requested dataset name.
- `dataset_version` (str, optional): Requested version of the Dataset.
- `only_completed` (bool, optional): Return only the completed dataset.
- `auto_create` (bool, optional): If the search result is empty and the filter is based on the dataset_name, create a new dataset.

**Returns**

- `Dataset`: Returns a Dataset object.

**Raises**

- `ValueError`: If the selection criteria are not met. Didn't provide id/name correctly.
- `ValueError`: If the query result is empty, it means that no dataset matching the provided selection criteria could be found.

### get_local_copy (internal dataset)

After finalizing the dataset, you have the option to download a local copy of it for further use. This local copy includes all the files of the dataset, including the parent dataset files, all conveniently placed in a single folder. If the dataset version is not explicitly specified in the download parameters, the dataset with the highest semantic version will be used.

```python
my_dataset = DatasetClient.get(dataset_name="my_dataset")
dataset.get_local_copy()
```

**Parameters**

- `verbose` (bool, optional): If True, enable console output for progress information by default it relies on `DatasetClient.verbose`(enabled by defaults) you can disable it by changing the value of DatasetClient.verbose  (`DatasetClient.verbose = False`).

**Returns**

- `none`: Does not return any results.


**Raises**

- `Exception`: If the dataset is in a final state, which includes `completed`, `aborted`, or `failed`.
- `Exception`: If we are unable to unzip a compressed file.
- `Exception`: If we encounter a failure while attempting to copy a file from a source folder to a target folder.

### add_aws_storage_conf 

This function configures interactions with AWS storage services, like Amazon S3, enabling the DatasetClient to retrieve and store data seamlessly. It's essential for the migration process to use this function before transferring data from AWS storage services.

```python 
from oip_dateset_client.Storage.StorageManager import StorageManager

StorageManager.add_aws_storage_conf(access_key=<your_access_key>,secret_key=<your_secret_key>,region=<region>)

```

**Parameters** 

- `access_key` (str, required): The access key is a unique identifier that allows access to AWS services and resources.
- `secret_key` (str, required): The secret key is a confidential piece of information used in conjunction with the access key for secure access to AWS services.
- `region` (str, required): The region specifies the geographical location where AWS resources will be provisioned or operated.


**Returns**

- `none`: Does not return any results.


### migrate

Make the most of our migration function if you have datasets stored in one of the supported cloud providers (currently AWS). This streamlined feature empowers you to effortlessly upload all files from your existing datasets to our OIP storage provider, simultaneously creating a new dataset. By doing so, you can unlock the full capabilities of our Dataset Client with your existing datasets.

**Parameters**

- `storage_conf_name` (str, required): storage configuration name serve as an identifier.
- `download_uri` (str, required): Refers to the specific location or path
    within the storage provider where the dataset files are hosted.              
- `name` (str, required): Name of the new dataset.
- `parent_datsets` (list[str], optional):  A list of parent datasets to extend the new dataset 
by adding all the files from their respective parent datasets.
- `version` (str, optional): Version of the new dataset, if no version is specified during creation, the default version will be set to 1.0.0  for the dataset's First version. For the next versions, we will automatically increment the highest semantic version available.
- `is_main` (bool, optional): True if the new dataset is the main version.
- `tags` (list[str], optional): Descriptive tags categorize datasets by keywords, detailing their subject matter, domain, or specific topics for better identification and organization.
- `description` (str, optional): A brief description of the new dataset.
- `verbose` (bool, optional): If True, enable console output for progress information by default it relies on `DatasetClient.verbose`(enabled by defaults) you can disable it by changing the value of DatasetClient.verbose  (`DatasetClient.verbose = False`).

**Returns**

- `none`: Does not return any results.

**Raises**

- `ValueError`: If the `name` is empty or `None`.
- `ValueError`: If any of the `parent_datasets` is not completed.

### get_local_copy (external dataset)

To include external files in your dataset (files that aren't present either locally or in our internal datasets), you should download them initially. Once downloaded, you can proceed to create your dataset and add the files you've obtained.
```python
from oip_dateset_client.dataset import DatasetClient
from oip_dateset_client.Storage.StorageManager import StorageManager

cifar_path = "https://www.cs.toronto.edu/~kriz/cifar-10-python.tar.gz"
local_path=StorageManager.get_local_copy(remote_url=cifar_path)
my_dataset = DatasetClient.create(name="my_dataset")
# add files   
my_dataset.add_files(path=local_path) 
my_dataset.upload()
# if the files are not uploaded yet
# we can use the auto_upload=true ie my_dataset.finalize(auto_upload=true)
my_dataset.finalize()
```

**Parameters**

- `remote_path` (str, required): Dataset url.
- `target_folder` (str, optional): The local directory where the dataset will be downloaded.
- `extract_archive` (bool, optional): If true, and the file is compressed, proceed to extract it. Defaults to True.

**Returns**

- `str`: path to the downloaded file.


**Raises**

- `Exception`: If we encounter a failure while attempting to download the requested file.
- `Exception`: If we are unable to unzip a compressed file.
q