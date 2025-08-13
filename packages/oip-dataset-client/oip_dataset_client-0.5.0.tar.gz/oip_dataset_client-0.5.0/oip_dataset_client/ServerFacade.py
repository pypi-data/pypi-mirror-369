import os
from typing import Dict, Optional, Union, Callable
from .HttpClient import HttpClient
from .schema import EntityListInstances, DatasetDict, ApiRequestArgs
from typeguard import typechecked
from .logger import Logger
from .ServerConf import SERVER_MODULE_NAME
from .utils import generate_url

logger = Logger().get_logger()


class ServerFacade:
    # the module that processes client requests on the server side.
    __server_module_name: str = SERVER_MODULE_NAME

    @classmethod
    @typechecked
    def save_data(
        cls,
        method: str,
        data: DatasetDict,
        dataset_entity_name: str,
    ):
        """
        Save the data on the server
        :param method: str: "Create" a new record if it doesn't exist, or "update" an existing record.
        :param data: DatasetDict: Data we need to create or update.
        :param dataset_entity_name: str: dataset entity name.
        :return: response content
        """
        logger.debug("call save_data")

        if method not in ["create", "update"]:
            raise ValueError(f"METHOD {method} IS NOT ALLOWED")

        crud_to_http_method = {"create": "post", "update": "put"}
        crud_to_url_suffix = {"create": "add", "update": "update"}

        base_url = generate_url(
            os.environ["OIP_API_HOST"],
            [cls.__server_module_name, dataset_entity_name,
                crud_to_url_suffix.get(method)],
        )

        headers: Dict = {"authorization": "APIKey " +
                         os.environ["OIP_API_KEY"]}

        _http_method: Callable = getattr(
            HttpClient, crud_to_http_method.get(method))
        response = _http_method(url=base_url, json=data, headers=headers)

        if response.status_code == 200:
            return response.json()

    @classmethod
    @typechecked
    def get_data(
        cls,
        entity: str,
        api_request_args: ApiRequestArgs,
    ) -> Optional[EntityListInstances]:
        """
        Retrieve data from the API based on the provided parameters.

        :param entity: str: The name of the entity for which to retrieve the data.
        :param api_request_args:api_request_args: Additional parameters for the API request.
        :return: list: The retrieved data.
        """
        url: str = os.path.join(
            os.environ["OIP_API_HOST"], cls.__server_module_name, entity
        )
        url = url.replace("\\", "/")
        headers: Dict[str, str] = {
            "authorization": "APIKey " + os.environ["OIP_API_KEY"]
        }
        resp = HttpClient.get(url, headers, api_request_args)
        if resp.status_code == 200:
            return resp.json()["data"]
        return None

    @classmethod
    @typechecked
    def create_presigned_post_url(
        cls,
        object_name: str,
    ) -> Optional[Dict[str, Union[str, Dict[str, Union[str, Dict[str, str]]]]]]:
        """
        Generate a pre-signed URL for uploading an object to the cloud storage.
        :param object_name: str: The name of the object to create a pre-signed URL for.
        :return:dict: information about the presigned url
        """
        url: str = os.path.join(
            os.environ["OIP_API_HOST"], cls.__server_module_name)
        url = os.path.join(url, "presigned_post_url")
        url = url.replace("\\", "/")
        headers: Dict = {"authorization": "APIKey " +
                         os.environ["OIP_API_KEY"]}
        data: Dict = {"object_name": object_name}
        resp = HttpClient.post(url=url, json=data, headers=headers)
        if resp.status_code == 200:
            return resp.json()
        return None

    @classmethod
    @typechecked
    def create_presigned_get_url(
        cls,
        object_name: str,
    ) -> Optional[str]:
        """
        Generate a pre-signed URL for downloading an object from the cloud storage.
        :param object_name: str: The name of the object to create a pre-signed URL for.
        :return:str: presigned get url
        """
        url: str = os.path.join(
            os.environ["OIP_API_HOST"], cls.__server_module_name)

        url = os.path.join(url, "presigned_get_url")
        url = url.replace("\\", "/")
        headers: Dict = {"authorization": "APIKey " +
                         os.environ["OIP_API_KEY"]}
        data: Dict = {"object_name": object_name}
        resp = HttpClient.post(url=url, json=data, headers=headers)
        if resp.status_code == 200:
            return resp.json()
        return None

    @classmethod
    @typechecked
    def tag_dataset_as_main(
        cls,
        dataset_id: str,
        dataset_entity_name: str,
    ) -> None:
        """
        Tag current dataset as the main version, at the same time
        removing the tag from the previous main version.
        :param dataset_id: str: id of the dataset we are looking to tag as main
        :param dataset_entity_name: str: dataset entity name
        :return: none
        """
        url: str = os.path.join(
            os.environ["OIP_API_HOST"],
            cls.__server_module_name,
            dataset_entity_name,
            "tag_as_main",
            "id",
            dataset_id,
        )
        headers: Dict[str, str] = {
            "authorization": "APIKey " + os.environ["OIP_API_KEY"]
        }
        HttpClient.put(url=url, headers=headers)
