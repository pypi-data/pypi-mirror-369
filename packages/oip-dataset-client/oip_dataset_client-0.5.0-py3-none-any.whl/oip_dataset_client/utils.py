import os
import hashlib
from functools import wraps
import json
from fnmatch import fnmatch
from dotenv import load_dotenv
from typing import Union, Optional, List, Tuple, Dict
from .logger import Logger
from typeguard import typechecked
from urllib.parse import urlunparse, urlsplit, urlencode

logger = Logger().get_logger()


def check_connection(func):
    """
    Decorator to check if required environment variables are set.
    If not set, attempt to load them from .env file.
    If still not set, raise an exception.
    """

    REQUIRED_ENV_VARS = [
        "OIP_API_HOST",
        "OIP_API_KEY",
        "OIP_WORKSPACE_NAME",
        "OIP_WORKSPACE_ID",
    ]

    def wrapper(*args, **kwargs):
        # Check if all required environment variables are set
        if all(var in os.environ for var in REQUIRED_ENV_VARS):
            return func(*args, **kwargs)

        # Attempt to load environment variables from .oip_dataset_env file
        load_dotenv(".oip_dataset_env")

        # Check again if all required environment variables are set
        if all(var in os.environ for var in REQUIRED_ENV_VARS):
            return func(*args, **kwargs)
        else:
            raise Exception(
                """Not connected, you must establish a connection either through the SDK using the connect function 
                or via the command line interface (CLI) by running oip-dataset-client-init."""
            )

    return wrapper


@typechecked
def check_storage_conf(storage_conf_name: str):
    """
    check if the storage configuration exist
    :param storage_conf_name: str: storage configuration name
    :return: none
    """
    if storage_conf_name not in os.environ:
        raise ValueError(
            f"Config {storage_conf_name} doesn't exist please add it before starting your migration."
        )
    # load storage configuration
    storage_conf: Dict[str, str] = json.loads(os.environ[storage_conf_name])

    if "PROVIDER" not in storage_conf:
        raise KeyError(
            "Provider information missing. Please review and re-add your configuration."
        )
    provider: str = storage_conf["PROVIDER"]

    providers_config_keys: Dict[str, List[str]] = {
        "AWS": ["ACCESS_KEY", "SECRET_KEY", "REGION"],
        "MINIO": ["HOST", "ACCESS_KEY", "SECRET_KEY"],
        "GCP": ["CREDENTIALS_JSON", "PROJECT", "ACCOUNT_NAME", "BUCKET"],
        "AZURE": ["ACCOUNT_NAME", "ACCOUNT_KEY", "BUCKET"],
    }

    if provider in providers_config_keys and not any(
        key in storage_conf for key in providers_config_keys[provider]
    ):
        raise Exception(
            f"Missing config for {storage_conf_name}. Please review and re-add your configuration."
        )
    elif provider not in providers_config_keys and provider != "OTHER":
        raise Exception(
            f"Provider {provider} doesn't exist. Please review and re-add your configuration."
        )


def sha256sum(
    filename: str, skip_header: Optional[int] = 0, block_size: Optional[int] = 65536
) -> Union[Tuple[str, str], Tuple[None, None]]:
    """
    create sha2 of the file, notice we skip the header of the file (32 bytes)
        because sometimes that is the only change
    :param filename: str: file name
    :param skip_header: int: default to 0 if 1 we skip
    :param block_size: int: default to 65536
    :return: union[(str,str),(none,none)]:
    """
    h = hashlib.sha256()
    file_hash = hashlib.sha256()
    b = bytearray(block_size)
    mv = memoryview(b)
    try:
        with open(filename, "rb", buffering=0) as f:
            # skip header
            if skip_header:
                file_hash.update(f.read(skip_header))
            for n in iter(lambda: f.readinto(mv), 0):
                h.update(mv[:n])
                if skip_header:
                    file_hash.update(mv[:n])
    except (Exception,):
        return None, None

    return h.hexdigest(), file_hash.hexdigest() if skip_header else None


def matches_any_wildcard(
    path: str, wildcards: Union[str, List], recursive: Optional[bool] = True
) -> bool:
    """
    Checks if given pattern matches any supplied wildcard

    :param path:str: path to check
    :param wildcards:union[str,list] wildcards to check against
    :param recursive: bool: whether or not the check is recursive. Default: True
        E.g. for path='directory/file.ext' and wildcards='*.ext',
        recursive=False will return False, but recursive=True will
        return True

    :return: bool: True if the path matches any wildcard and False otherwise
    """
    if wildcards is None:
        wildcards = ["*"]
    if not isinstance(wildcards, list):
        wildcards = [wildcards]
    wildcards = [str(w) for w in wildcards]
    if not recursive:
        path_as_list: List[str] = path.split("/")
    for wildcard in wildcards:
        if not recursive:
            wildcard = wildcard.split("/")
            matched: bool = True
            if len(path_as_list) != len(wildcard):
                continue
            for path_segment, wildcard_segment in zip(path_as_list, wildcard):
                if not fnmatch(path_segment, wildcard_segment):
                    matched = False
                    break
            if matched:
                return True
        else:
            wildcard_file: str = wildcard.split("/")[-1]
            wildcard_dir: str = wildcard[: -len(wildcard_file)] + "*"
            if fnmatch(path, wildcard_dir) and fnmatch(
                "/" + path, "*/" + wildcard_file
            ):
                return True
    return False


def format_size(
    size_in_bytes: Union[int, float],
    binary: Optional[bool] = False,
    use_nonbinary_notation: Optional[bool] = False,
    use_b_instead_of_bytes: Optional[bool] = False,
) -> str:
    """
    Return the size in human readable format (string)
    Matching humanfriendly.format_size outputs

    :param size_in_bytes:union[float,int]: number of bytes
    :param binary: bool: If `True` 1 Kb equals 1024 bytes, if False (default) 1 KB = 1000 bytes
    :param use_nonbinary_notation: bool: Only applies if binary is `True`. If this is `True`,
        the binary scale (KiB, MiB etc.) will be replaced with the regular scale (KB, MB etc.)
    :param use_b_instead_of_bytes: bool: If `True`, return the formatted size with `B` as the
        scale instead of `byte(s)` (when applicable)
    :return: string representation of the number of bytes (b,Kb,Mb,Gb, Tb,)
        >>> format_size(0)
        '0 bytes'
        >>> format_size(1)
        '1 byte'
        >>> format_size(5)
        '5 bytes'
        > format_size(1000)
        '1 KB'
        > format_size(1024, binary=True)
        '1 KiB'
        >>> format_size(1000 ** 3 * 4)
        '4 GB'
    """
    size: float = float(size_in_bytes)
    # single byte is the exception here
    if size == 1 and not use_b_instead_of_bytes:
        return "{} byte".format(int(size))
    k: int = 1024 if binary else 1000
    scale: List[str] = (
        ["bytes", "KiB", "MiB", "GiB", "TiB", "PiB"]
        if (binary and not use_nonbinary_notation)
        else ["bytes", "KB", "MB", "GB", "TB", "PB"]
    )
    if use_b_instead_of_bytes:
        scale[0] = "B"
    for i, m in enumerate(scale):
        if size < k ** (i + 1) or i == len(scale) - 1:
            return (
                (
                    "{:.2f}".format(size / (k**i)).rstrip("0").rstrip(".")
                    if i > 0
                    else "{}".format(int(size))
                )
                + " "
                + m
            )
    # we should never get here
    return f"{int(size)} {scale[0]}"


def is_within_directory(directory: str, target: str) -> bool:
    """
    Check if the path represented by 'target' is within or equal to the 'directory'.
    :param directory: str: The directory path to check against.
    :param target: str: The path to be checked.
    :return: bool: True if 'target' is within or equal to 'directory', False otherwise.
    """
    abs_directory = os.path.abspath(directory)
    abs_target = os.path.abspath(target)
    prefix = os.path.commonprefix([abs_directory, abs_target])
    return prefix == abs_directory


def generate_url(
        base_url: str,
        path_segments: list,
        query_params: dict = None
) -> str:
    """
    Generate a URL from base_url, path_segments, and query_params.

    Args:
    - base_url (str): The base URL including the scheme and netloc.
    - path_segments (list): List of path segments to be appended to the base URL.
    - query_params (dict, optional): Dictionary of query parameters to be appended to the URL.

    Returns:
    - str: The generated URL.
    """

    def _build_path_from_segments(segments: list) -> str:
        if not segments:
            return ''
        url = '/'.join([segment.strip('/') for segment in segments])
        if segments and segments[-1].endswith('/'):
            url += '/'
        return url

    split_url = urlsplit(
        base_url.strip('/')
    )

    scheme = split_url.scheme or 'https'

    netloc = f"{split_url.netloc}{split_url.path}"

    path = _build_path_from_segments(path_segments)

    query = urlencode(query_params) if query_params else ''

    url_components = (scheme, netloc, path, '', query, '')

    return urlunparse(url_components)
