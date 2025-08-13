from typing import Optional
from ..HttpClient import HttpClient
from ..ServerFacade import ServerFacade
import tempfile
import json
from pathlib import Path
import os
import requests
from urllib.parse import urlparse
from typing import Dict, Union
import shutil
from time import time
from ..schema import DatasetState
from ..logger import Logger
from typeguard import typechecked

from .AwsProvider import AwsProvider
from .GcpProvider import GcpProvider
from .AzureProvider import AzureProvider
from .MinioProvider import MinioProvider


logger = Logger().get_logger()

COMPRESSED_EXTENSION = [
    ".zip",
    ".gz",
    ".tar.gz",
    ".bz2",
    ".7z",
    ".rar",
    ".tar",
    ".zst",
    ".xz",
    ".Z",
    ".sit",
    ".sitx",
]


class StorageManager:
    __default_target_folder = "global"
    # in MB
    __chunk_size = 5

    @classmethod
    def __verify(cls) -> bool:
        return os.environ.get("OI_REQUESTS_VERIFY_SSL", "true").lower() in ("1", "true")

    @staticmethod
    @typechecked
    def upload_state(object_name: str, dataset_state: DatasetState):
        """
        Upload state file to the cloud storage
        :param object_name: str: object name
        :param dataset_state: DatasetState: dataset state
        """
        logger.debug("call upload_state")
        presigned_post_data: Optional[
            Dict[str, Union[str, Dict[str, Union[str, Dict[str, str]]]]]
        ] = ServerFacade.create_presigned_post_url(object_name)
        if type(presigned_post_data) is dict:
            if type(presigned_post_data["kwargs"]) is dict:
                if type(presigned_post_data["kwargs"]["url"]) is str:
                    url: str = presigned_post_data["kwargs"]["url"]
                if (
                    "data" in presigned_post_data["kwargs"]
                    and type(presigned_post_data["kwargs"]["data"]) is dict
                ):
                    data: Dict[str, str] = presigned_post_data["kwargs"]["data"]
                else:
                    data = None
            if type(presigned_post_data["method"]) is str:
                upload_method: str = presigned_post_data["method"]

            with tempfile.NamedTemporaryFile(mode="w+") as temp_state_file:
                json.dump(dataset_state, temp_state_file, indent=4)
                temp_state_file.seek(0)
                if upload_method == "PUT":
                    binary_data = temp_state_file.read()
                    HttpClient.put(url=url, data=binary_data)
                elif upload_method == "POST":
                    file_ = {"file": (object_name, temp_state_file)}
                    HttpClient.post(
                        url=url,
                        data=data,
                        files=file_,
                    )

    @staticmethod
    @typechecked
    def upload(object_name: str, path: str) -> bool:
        """
        Upload data file to the cloud storage
        :param object_name: str: object name
        :param path: str: path to the file
        :return: bool:
        """
        presigned_post_data: Optional[
            Dict[str, Union[str, Dict[str, Union[str, Dict[str, str]]]]]
        ] = ServerFacade.create_presigned_post_url(object_name)
        if type(presigned_post_data) is dict:
            if type(presigned_post_data["kwargs"]) is dict:
                if type(presigned_post_data["kwargs"]["url"]) is str:
                    url: str = presigned_post_data["kwargs"]["url"]
                if (
                    "data" in presigned_post_data["kwargs"]
                    and type(presigned_post_data["kwargs"]["data"]) is dict
                ):
                    data: Dict[str, str] = presigned_post_data["kwargs"]["data"]
                else:
                    data = None
            if type(presigned_post_data["method"]) is str:
                upload_method: str = presigned_post_data["method"]
            with open(path, "rb") as file:
                if upload_method == "PUT":
                    binary_data = file.read()
                    HttpClient.put(url=url, data=binary_data)
                else:
                    file_ = {"file": (object_name, file)}

                    HttpClient.post(
                        url=url,
                        data=data,
                        files=file_,
                    )

            return True
        return False

    @staticmethod
    @typechecked
    def download(object_name: str, download_path: str) -> Optional[str]:
        """
        Download data file from the cloud storage
        :param object_name: str: object name
        :param download_path: str: download location
        :return: bool:
        """
        presigned_get_data: Optional[str] = ServerFacade.create_presigned_get_url(
            object_name
        )
        if type(presigned_get_data) is str:
            get_url: str = presigned_get_data
            response = HttpClient.get(get_url)
            if response.status_code == 200:
                with open(download_path, "wb") as file:
                    file.write(response.content)
                return download_path
        return None

    @staticmethod
    @typechecked
    def download_state(object_name: str) -> Optional[DatasetState]:
        """
        Download state file from the cloud storage
        :param object_name: str: object name
        :return: DatasetState: dataset state
        """
        presigned_get_data: Optional[str] = ServerFacade.create_presigned_get_url(
            object_name
        )
        if type(presigned_get_data) is str:
            get_url: str = presigned_get_data
            response = HttpClient.get(get_url)
            if response.status_code == 200:
                return response.json()

        return None

    @classmethod
    @typechecked
    def get_local_copy(
        cls,
        remote_url: str,
        target_folder: Optional[str] = None,
        extract_archive: Optional[bool] = True,
    ) -> str:
        """
        Get a local copy of a external dataset (dataset that doesn't belong to our storage)
        :param remote_url: str: dataset url
        :type target_folder: str: the local directory where the dataset will be downloaded.
        :param extract_archive: bool: if true extract the compressed file (defaults to True)
        :return: str: path to the downloaded file
        """
        # Parse the URL to extract the path, which includes the filename.
        url_parts = urlparse(remote_url)
        remote_path = url_parts.path
        file_name = remote_path.split("/")[-1]
        if not target_folder:
            target_folder = cls.__default_target_folder
        # we download into temp_local_path so that if we accidentally stop in the middle,
        # we won't think we have the entire file
        timestamp = str(time()).replace(".", "")
        temp_target_folder: str = f"{target_folder}_{timestamp}_partially"
        temp_dst_file_path: str = os.path.join(temp_target_folder, file_name)
        Path(temp_target_folder).mkdir(parents=True, exist_ok=True)

        with requests.get(url=remote_url, stream=True, verify=cls.__verify()) as response:
            try:
                with open(temp_dst_file_path, mode="wb") as file:
                    for chunk in response.iter_content(
                        chunk_size=cls.__chunk_size * 1024
                    ):
                        file.write(chunk)
            except (Exception,):
                shutil.rmtree(temp_target_folder)
                raise Exception("failed in downloading file")

        suffix: str = Path(temp_dst_file_path).suffix.lower()
        if suffix == ".gz":
            suffix = "".join(a.lower()
                             for a in Path(temp_dst_file_path).suffixes[-2:])
        if extract_archive and suffix in COMPRESSED_EXTENSION:
            try:
                unzipped_folder = file_name[: -len(suffix)]
                path_to_unzipped_temp_target_folder: str = (
                    f"{temp_target_folder}/{unzipped_folder}"
                )
                shutil.unpack_archive(
                    temp_dst_file_path, path_to_unzipped_temp_target_folder
                )
                os.remove(temp_dst_file_path)
                path_to_unzipped_target_folder = f"{target_folder}/{unzipped_folder}"
                count_suffix: int = 0
                # in case we already download the dataset
                while os.path.exists(path_to_unzipped_target_folder):
                    count_suffix += 1
                    path_to_unzipped_target_folder = (
                        f"{target_folder}/{unzipped_folder}-{str(count_suffix)}"
                    )
                shutil.move(path_to_unzipped_temp_target_folder, target_folder)
                shutil.rmtree(temp_target_folder)
                return path_to_unzipped_target_folder
            except Exception as e:
                shutil.rmtree(temp_target_folder)
                raise Exception(e)
        # not a compressed file
        else:
            dst_file_path: str = f"{target_folder}/{file_name}"
            if os.path.exists(dst_file_path):
                base_file_name: str = file_name[: -len(suffix)]
                dst_file_path = f"{target_folder}/{base_file_name}-1{suffix}"
                count_suffix = 1
                while os.path.exists(dst_file_path):
                    count_suffix += 1
                    dst_file_path = (
                        f"{target_folder}/{base_file_name}-{str(count_suffix)}{suffix}"
                    )
                os.rename(
                    temp_dst_file_path,
                    f"{temp_target_folder}/{base_file_name}-{count_suffix}{suffix}",
                )
                temp_dst_file_path = (
                    f"{temp_target_folder}/{base_file_name}-{count_suffix}{suffix}"
                )

                shutil.move(temp_dst_file_path, target_folder)

            else:
                os.rename(temp_dst_file_path, dst_file_path)
            shutil.rmtree(temp_target_folder)
            return dst_file_path

    @staticmethod
    @typechecked
    def add_aws_storage_conf(
        storage_conf_name: str, access_key: str, secret_key: str, region: str
    ):
        """
        Add AWS storage configuration. You can include one or multiple AWS configurations
            by recalling this function.
        :param storage_conf_name: str: storage configuration name serve as an identifier.
        :param access_key: str: aws access key
        :param secret_key: str: aws secret key
        :param region: str: aws region
        :return: none:
        """
        aws_conf: Dict[str, str] = {
            "PROVIDER": "AWS",
            "ACCESS_KEY": access_key,
            "SECRET_KEY": secret_key,
            "REGION": region,
        }

        os.environ[storage_conf_name] = json.dumps(aws_conf)

    @classmethod
    @typechecked
    def download_via_storage_provider(
        cls,
        storage_conf_name: str,
        download_uri: str,
        download_folder: str,
        max_workers: int,
        verbose: bool,
    ):
        """
        Download all the dataset files located in a specific download_uri
        :param storage_conf_name: str: storage configuration name serve as an identifier.
        :param download_uri: str: uri from where we download the dataset files refers to the specific location or path
            within the storage provider where the dataset files are hosted.
            The following are examples of ``download_uri``
             - S3: s3://bucket/folder/../dataset_folder
             - Google Cloud Storage: gs://bucket/folder/../dataset_folder
             - Azure Storage: azure://bucket/folder/../dataset_folder
             - Minio Storage: minio://bucket/folder/../dataset_folder
             - Other https://path_to_the_dataset_folder
        :param download_folder: str: destination directory  or folder where downloaded files will be stored.
        :param max_workers: int:Numbers of threads to be spawned when zipping and uploading the files.
            If None number of logical cores
        :param verbose: bool: If True, enable console output for progress information (defaults to true)
        :return: str: path to the downloaded dataset directory
        """
        provider_mapping = {
            "AWS": AwsProvider,
            "GCP": GcpProvider,
            "AZURE": AzureProvider,
            "MINIO": MinioProvider,
        }
        # load storage conf
        storage_conf: Dict[str, str] = json.loads(
            os.environ[storage_conf_name])
        provider: str = storage_conf["PROVIDER"]
        if provider in provider_mapping:
            return provider_mapping[provider].download(
                storage_conf_name, download_uri, download_folder, max_workers, verbose
            )
        elif provider == "OTHER" and download_uri.startswith("http"):
            return cls.get_local_copy(download_uri, download_folder)
        else:
            raise ValueError(
                f"{provider} is not a valid provider please check the  official documentation"
            )
