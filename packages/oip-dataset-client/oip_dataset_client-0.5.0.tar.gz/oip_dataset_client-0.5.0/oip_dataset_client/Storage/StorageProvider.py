from abc import ABC, abstractmethod
from typeguard import typechecked


class StorageProvider(ABC):
    @staticmethod
    @abstractmethod
    @typechecked
    def download(
        storage_conf_name: str,
        download_uri: str,
        download_folder: str,
        max_workers: int,
        verbose: bool,
    ) -> str:
        """
        Download all the dataset files located in a specific download_uri
        :param storage_conf_name: str: storage configuration name serve as an identifier.
        :param download_uri: str: uri from where we download the dataset files refers to the specific location or path
            within the storage provider where the dataset files are hosted.
            example s3://bucket/folder/../dataset_folder
        :param download_folder: str: destination directory or folder where downloaded files will be stored.
        :param max_workers: int:Numbers of threads to be spawned when zipping and uploading the files.
            If None number of logical cores
        :param verbose: bool: If True, enable console output for progress information (defaults to true)
        :return: str: path to the downloaded dataset directory
        """
        pass
