""" Open Innovation Dataset Client configuration wizard"""

import os
from typing import Dict, Optional
from oip_dataset_client.HttpClient import HttpClient
from oip_dataset_client.schema import ApiRequestArgs
from oip_dataset_client.ServerConf import SERVER_MODULE_NAME, WORKSPACE_ENTITY_NAME
from oip_dataset_client.logger import Logger

logger = Logger().get_logger()


def main():
    """setting up the oip-dataset-client"""

    print("Open Innovation Dataset SDK setup process")
    oip_credentials = prompt_oip_credentials()
    with open(".oip_dataset_env", "w") as env_file:

        if oip_credentials:
            env_file.write(f"OIP_API_HOST={oip_credentials['api_host']}{os.linesep}")
            env_file.write(f"OIP_API_KEY={oip_credentials['api_key']}{os.linesep}")
            env_file.write(
                f"OIP_WORKSPACE_ID={oip_credentials['workspace_id']}{os.linesep}"
            )
            env_file.write(
                f"OIP_WORKSPACE_NAME={oip_credentials['workspace_name']}{os.linesep}"
            )
            logger.info("Connection to the server successful. Welcome!")


def prompt_oip_credentials() -> Optional[Dict[str, str]]:
    """
    :return: dict: open innovation credentials example:
        {api_host:oip_host,
        api_key:your_api_key,
        workspace_name:your_workspace_name,
        workspace_id:your_workspace_id}
    """
    description = (
        "\n"
        "Please navigate to the Workspace page within the `Open Innovation web application`.\n"
        "Select your desired workspace, then click on `Create new credentials`.\n"
        "Afterward, click on `Copy to clipboard.` Finally, paste the copied configuration here:\n"
    )
    print(description)
    # parse input to dict
    try:
        oip_credentials: Dict[str, str] = {}
        # Iterate over input until encountering "}"
        while True:
            line = input().strip()
            if line == "}":
                break
            if "=" in line:
                key, value = map(str.strip, line.split("="))
                value = value.replace('"', "")
                oip_credentials[key] = value
    except:
        raise Exception(
            "You need to copy and paste the correct configuration exactly as it appears on the website"
        )

    api_host: str = oip_credentials.get("api_host", "")
    api_key: str = oip_credentials.get("api_key", "")
    workspace_name: str = oip_credentials.get("workspace", "")
    # print message to the consol and exist if any issue happen
    workspace_id: Optional[str] = get_workspace_id(api_host, api_key, workspace_name)
    if workspace_id:
        oip_credentials["workspace_id"] = workspace_id
        return oip_credentials
    else:
        return None


def get_workspace_id(api_host: str, api_key: str, workspace_name: str) -> Optional[str]:
    """
    Retrieve workspace id from the server api based on the provided parameters.
    :param api_host: str: The API Host
    :param api_key: str: The API Key
    :param workspace_name: str: The workspace name
    :return: str: Workspace ID.
    """
    url: str = os.path.join(api_host, SERVER_MODULE_NAME, WORKSPACE_ENTITY_NAME)
    url = url.replace("\\", "/")
    headers: Dict[str, str] = {"authorization": "APIKey " + api_key}
    api_request_args: ApiRequestArgs = {
        "filter_cols": "name",
        "filter_ops": "=",
        "filter_vals": workspace_name,
    }
    response = HttpClient.get(url, headers, api_request_args)
    if response.status_code == 200 and response.json()["data"]:
        return response.json()["data"][0]["id"]
    else:
        print(
            f"{workspace_name} is not a valid workspace please verify it and try again"
        )
        exit(1)


if __name__ == "__main__":
    main()
