import os
import json
import boto3
from tqdm import tqdm
from typeguard import typechecked
from pathlib import Path
from .StorageProvider import StorageProvider
from concurrent.futures import ThreadPoolExecutor
from typing import Dict


class AwsProvider(StorageProvider):
    @staticmethod
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
        aws_conf: Dict[str, str] = json.loads(os.environ[storage_conf_name])
        session: boto3.Session = boto3.Session(
            aws_access_key_id=aws_conf["ACCESS_KEY"],
            aws_secret_access_key=aws_conf["SECRET_KEY"],
            region_name=aws_conf["REGION"],
        )
        s3 = session.resource("s3")

        bucket_name: str = download_uri[len("s3://") :].split("/")[0]
        object_to_download: str = download_uri[len(f"s3://{bucket_name}/") :]
        dataset_name: str = download_uri.split("/")[-2]
        bucket = s3.Bucket(bucket_name)
        bucket_objects = bucket.objects.filter(Prefix=object_to_download)

        with ThreadPoolExecutor(max_workers=max_workers) as pool:
            if verbose:
                download_prog_bar = tqdm(
                    total=len(list(bucket_objects)),
                    desc="downloading",
                    unit=" file ",
                )
            for obj in bucket_objects:
                file_path: Path = Path(obj.key)
                parent_folder: Path = Path(f"{download_folder}/{str(file_path.parent)}")
                if not parent_folder.exists():
                    parent_folder.mkdir(parents=True, exist_ok=True)
                download_task = pool.submit(
                    bucket.download_file,
                    str(file_path),
                    f"{download_folder}/{str(file_path)}",
                )
                if verbose:
                    download_task.add_done_callback(
                        lambda task: download_prog_bar.update(1)
                    )

        return f"{download_folder}/{object_to_download}"
