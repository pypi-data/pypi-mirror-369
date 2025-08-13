import os
import requests
import time
from typing import Dict, Optional, Union, Any
from .schema import DatasetDict
from .logger import Logger

logger = Logger().get_logger()


class HttpClient:
    MAX_RETRIES: int = 4

    @classmethod
    def __verify(cls) -> bool:
        return os.environ.get("OI_REQUESTS_VERIFY_SSL", "true").lower() in ("1", "true",)

    @classmethod
    def get(
        cls,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, str]] = None,
        stream: Optional[bool] = False,
    ):
        """
        General get request function.
        Assigns headers and builds in retries and logging
        :param url: str: api host, example: https://www.example.com/api?x=1
        :param headers: Dict[str, str]: headers
        :param params: Dict[str, str]: params
        :param stream: bool:
        """
        """General 'make api request' function.
      Assigns headers and builds in retries and logging.
      """
        logger.debug(f"call http get method (url:{url})")
        base_log_record: Dict[str, Union[str, Dict[str, str]]] = dict(
            route=url, params=params
        )
        retry_count: int = 0

        while retry_count <= cls.MAX_RETRIES:
            start_time: float = time.time()
            try:
                response: Union[requests.Response, Exception] = requests.get(
                    url, params=params, headers=headers, timeout=None, stream=stream, verify=cls.__verify()
                )
            except Exception as e:
                response = e

            elapsed_time: float = time.time() - start_time
            status_code: int = (
                response.status_code if hasattr(
                    response, "status_code") else None
            )
            log_record: Dict[str, Union[int, float, str, Dict[str, str]]] = dict(
                base_log_record
            )
            log_record["elapsed_time_in_ms"] = 1000 * elapsed_time
            log_record["retry_count"] = retry_count
            log_record["status_code"] = status_code
            if status_code == 200:  # Success
                logger.debug("OK", extra=log_record)
                return response
            if status_code in [204, 206]:  # Success with a caveat - warning
                log_msg = {204: "No Content",
                           206: "Partial Content"}[status_code]
                logger.warning(log_msg, extra=log_record)
                return response
            log_record["tag"] = "failed_gro_api_request"
            if retry_count < cls.MAX_RETRIES:
                logger.warning(
                    response.text if hasattr(response, "text") else response,
                    extra=log_record,
                )
            if status_code in [400, 401, 402, 404, 301]:
                break  # Do not retry
            logger.warning("{}".format(response), extra=log_record)
            if retry_count > 0:
                # Retry immediately on first failure.
                # Exponential backoff before retrying repeatedly failing requests.
                time.sleep(2**retry_count)
            retry_count += 1
        raise APIError(response, retry_count, url)

    @classmethod
    def post(
        cls,
        url: str,
        data: Optional[Union[DatasetDict, Dict[str, str]]] = None,
        json=None,
        headers: Optional[Dict[str, str]] = None,
        files: Optional[Dict] = None,
        stream: Optional[bool] = False,
    ):
        """
        General post request function.
        Assigns headers and builds in retries and logging
        :param url: str: api host, example: https://www.example.com/api?x=1
        :param headers: Dict[str, str]: headers
        :param data: Dict[str, str]: params
        :param json: json data
        :param files: files
        :param stream: bool:
        """
        """General 'make api request' function.
     Assigns headers and builds in retries and logging.
     """
        logger.debug(f"call http post method (url {url})")
        base_log_record: Dict = dict(route=url, data=data)
        retry_count: int = 0

        while retry_count <= cls.MAX_RETRIES:
            start_time: float = time.time()
            try:
                if data:
                    response: Union[requests.Response, Exception] = requests.post(
                        url,
                        data=data,
                        headers=headers,
                        files=files,
                        timeout=None,
                        stream=stream,
                        verify=cls.__verify()
                    )
                else:
                    response = requests.post(
                        url,
                        json=json,
                        headers=headers,
                        files=files,
                        timeout=None,
                        stream=stream,
                        verify=cls.__verify()
                    )
            except Exception as e:
                response = e

            elapsed_time: float = time.time() - start_time
            status_code: int = (
                response.status_code if hasattr(
                    response, "status_code") else None
            )
            log_record: Dict[str, Union[int, float, str, Dict[str, str]]] = dict(
                base_log_record
            )
            log_record["elapsed_time_in_ms"] = 1000 * elapsed_time
            log_record["retry_count"] = retry_count
            log_record["status_code"] = status_code
            if status_code in [200, 204]:  # Success
                logger.debug("OK", extra=log_record)
                return response
            log_record["tag"] = "failed_gro_api_request"
            if retry_count < cls.MAX_RETRIES:
                logger.warning(
                    response.text if hasattr(response, "text") else response,
                    extra=log_record,
                )
            if status_code in [400, 401, 402, 404, 301]:
                break  # Do not retry
            logger.warning("{}".format(response), extra=log_record)
            if retry_count > 0:
                # Retry immediately on first failure.
                # Exponential backoff before retrying repeatedly failing requests.
                time.sleep(2**retry_count)
            retry_count += 1
        raise APIError(response, retry_count, url)

    @classmethod
    def put(
        cls,
        url: str,
        json: DatasetDict = None,
        data: Any = None,
        headers: Optional[Dict[str, str]] = None,
        stream: Optional[bool] = False,
    ):
        """
        General put request function.
        Assigns headers and builds in retries and logging
        :param url: str: api host, example: https://www.example.com/api?x=1
        :param headers: Dict[str, str]: headers
        :param json: json data
        :param data: Dict[str, str]: params
        :param stream: bool:
        """
        """General 'make api request' function.
      Assigns headers and builds in retries and logging.
      """
        logger.debug(f"call http put method (url {url})")
        base_log_record: Dict = dict(route=url, data=json)
        retry_count: int = 0
        while retry_count <= cls.MAX_RETRIES:
            start_time: float = time.time()
            try:
                if json:
                    response: Union[requests.Response, Exception] = requests.put(
                        url, json=json, headers=headers, timeout=None, stream=stream, verify=cls.__verify()
                    )
                else:
                    response = requests.put(
                        url, data=data, headers=headers, timeout=None, stream=stream, verify=cls.__verify()
                    )
            except Exception as e:
                response = e

            elapsed_time: float = time.time() - start_time
            status_code: int = (
                response.status_code if hasattr(
                    response, "status_code") else None
            )
            log_record: Dict[str, Union[int, float, str, Dict[str, str]]] = dict(
                base_log_record
            )
            log_record["elapsed_time_in_ms"] = 1000 * elapsed_time
            log_record["retry_count"] = retry_count
            log_record["status_code"] = status_code
            if status_code == 200:  # Success
                logger.debug("OK", extra=log_record)
                return response
            log_record["tag"] = "failed_gro_api_request"
            if retry_count < cls.MAX_RETRIES:
                logger.warning(
                    response.text if hasattr(response, "text") else response,
                    extra=log_record,
                )
            if status_code in [400, 401, 402, 404, 301]:
                break  # Do not retry
            logger.warning("{}".format(response), extra=log_record)
            if retry_count > 0:
                # Retry immediately on first failure.
                # Exponential backoff before retrying repeatedly failing requests.
                time.sleep(2**retry_count)
            retry_count += 1
        raise APIError(response, retry_count, url)


class APIError(Exception):
    def __init__(
        self,
        response,
        retry_count: int,
        url: str,
    ):
        self.response = response
        self.retry_count: int = retry_count
        self.url: str = url
        self.status_code = (
            response.status_code if hasattr(response, "status_code") else None
        )
        try:
            json_content = self.response.json()
            # 'error' should be something like 'Not Found' or 'Bad Request'
            self.message: str = json_content.get("error", "")
            # Some error responses give additional info.
            # For example, a 400 Bad Request might say "metricId is required"
            if "message" in json_content:
                self.message += ": {}".format(json_content["message"])
        except (Exception,):
            # If the error message can't be parsed, fall back to a generic "giving up" message.
            self.message = "Giving up on {} after {} {}: {}".format(
                self.url,
                self.retry_count,
                "retry" if self.retry_count == 1 else "retries",
                response,
            )
