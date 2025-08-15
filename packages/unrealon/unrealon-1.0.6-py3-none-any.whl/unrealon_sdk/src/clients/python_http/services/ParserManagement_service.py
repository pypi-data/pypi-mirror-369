import json
from typing import *

import httpx

from ..api_config import APIConfig, HTTPException
from ..models import *


def list_parsers_api_v1_parsers__get(
    authorization: Optional[str] = None, api_config_override: Optional[APIConfig] = None
) -> SuccessResponse:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f"/api/v1/parsers/"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Bearer { api_config.get_access_token() }",
        **({"authorization": authorization} if authorization is not None else {}),
    }
    query_params: Dict[str, Any] = {}

    query_params = {key: value for (key, value) in query_params.items() if value is not None}

    with httpx.Client(base_url=base_path, verify=api_config.verify) as client:
        response = client.request(
            "get",
            httpx.URL(path),
            headers=headers,
            params=query_params,
        )

    if response.status_code != 200:
        raise HTTPException(response.status_code, f" failed with status code: {response.status_code}")

    return SuccessResponse(**response.json()) if response.json() is not None else SuccessResponse()


def register_parser_api_v1_parsers_register_post(
    data: ParserRegistrationRequest,
    authorization: Optional[str] = None,
    api_config_override: Optional[APIConfig] = None,
) -> ParserRegistrationResponse:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f"/api/v1/parsers/register"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Bearer { api_config.get_access_token() }",
        **({"authorization": authorization} if authorization is not None else {}),
    }
    query_params: Dict[str, Any] = {}

    query_params = {key: value for (key, value) in query_params.items() if value is not None}

    with httpx.Client(base_url=base_path, verify=api_config.verify) as client:
        response = client.request("post", httpx.URL(path), headers=headers, params=query_params, json=data.model_dump())

    if response.status_code != 201:
        raise HTTPException(response.status_code, f" failed with status code: {response.status_code}")

    return (
        ParserRegistrationResponse(**response.json()) if response.json() is not None else ParserRegistrationResponse()
    )


def get_parser_api_v1_parsers__parser_id__get(
    parser_id: str, authorization: Optional[str] = None, api_config_override: Optional[APIConfig] = None
) -> SuccessResponse:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f"/api/v1/parsers/{parser_id}"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Bearer { api_config.get_access_token() }",
        **({"authorization": authorization} if authorization is not None else {}),
    }
    query_params: Dict[str, Any] = {}

    query_params = {key: value for (key, value) in query_params.items() if value is not None}

    with httpx.Client(base_url=base_path, verify=api_config.verify) as client:
        response = client.request(
            "get",
            httpx.URL(path),
            headers=headers,
            params=query_params,
        )

    if response.status_code != 200:
        raise HTTPException(response.status_code, f" failed with status code: {response.status_code}")

    return SuccessResponse(**response.json()) if response.json() is not None else SuccessResponse()


def delete_parser_api_v1_parsers__parser_id__delete(
    parser_id: str, authorization: Optional[str] = None, api_config_override: Optional[APIConfig] = None
) -> None:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f"/api/v1/parsers/{parser_id}"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Bearer { api_config.get_access_token() }",
        **({"authorization": authorization} if authorization is not None else {}),
    }
    query_params: Dict[str, Any] = {}

    query_params = {key: value for (key, value) in query_params.items() if value is not None}

    with httpx.Client(base_url=base_path, verify=api_config.verify) as client:
        response = client.request(
            "delete",
            httpx.URL(path),
            headers=headers,
            params=query_params,
        )

    if response.status_code != 204:
        raise HTTPException(response.status_code, f" failed with status code: {response.status_code}")

    return None


def execute_parser_command_api_v1_parsers__parser_id__commands_post(
    parser_id: str,
    data: ParserCommandRequest,
    authorization: Optional[str] = None,
    api_config_override: Optional[APIConfig] = None,
) -> SuccessResponse:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f"/api/v1/parsers/{parser_id}/commands"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Bearer { api_config.get_access_token() }",
        **({"authorization": authorization} if authorization is not None else {}),
    }
    query_params: Dict[str, Any] = {}

    query_params = {key: value for (key, value) in query_params.items() if value is not None}

    with httpx.Client(base_url=base_path, verify=api_config.verify) as client:
        response = client.request("post", httpx.URL(path), headers=headers, params=query_params, json=data.model_dump())

    if response.status_code != 202:
        raise HTTPException(response.status_code, f" failed with status code: {response.status_code}")

    return SuccessResponse(**response.json()) if response.json() is not None else SuccessResponse()


def get_parser_status_api_v1_parsers__parser_id__status_get(
    parser_id: str, authorization: Optional[str] = None, api_config_override: Optional[APIConfig] = None
) -> SuccessResponse:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f"/api/v1/parsers/{parser_id}/status"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Bearer { api_config.get_access_token() }",
        **({"authorization": authorization} if authorization is not None else {}),
    }
    query_params: Dict[str, Any] = {}

    query_params = {key: value for (key, value) in query_params.items() if value is not None}

    with httpx.Client(base_url=base_path, verify=api_config.verify) as client:
        response = client.request(
            "get",
            httpx.URL(path),
            headers=headers,
            params=query_params,
        )

    if response.status_code != 200:
        raise HTTPException(response.status_code, f" failed with status code: {response.status_code}")

    return SuccessResponse(**response.json()) if response.json() is not None else SuccessResponse()
