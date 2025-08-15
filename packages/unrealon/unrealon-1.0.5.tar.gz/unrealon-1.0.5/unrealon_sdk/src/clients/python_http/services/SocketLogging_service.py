import json
from typing import *

import httpx

from ..api_config import APIConfig, HTTPException
from ..models import *


def add_log_entry_api_v1_logging_log_post(
    data: LoggingRequest,
    authorization: Optional[str] = None,
    api_config_override: Optional[APIConfig] = None,
) -> LoggingResponse:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f"/api/v1/logging/log"
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

    if response.status_code != 200:
        raise HTTPException(response.status_code, f" failed with status code: {response.status_code}")

    return LoggingResponse(**response.json()) if response.json() is not None else LoggingResponse()


def list_developer_sessions_api_v1_logging_sessions_get(
    authorization: Optional[str] = None, api_config_override: Optional[APIConfig] = None
) -> SuccessResponse:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f"/api/v1/logging/sessions"
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


def start_logging_session_api_v1_logging_sessions_start_post(
    data: SessionStartRequest,
    authorization: Optional[str] = None,
    api_config_override: Optional[APIConfig] = None,
) -> LoggingResponse:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f"/api/v1/logging/sessions/start"
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

    if response.status_code != 200:
        raise HTTPException(response.status_code, f" failed with status code: {response.status_code}")

    return LoggingResponse(**response.json()) if response.json() is not None else LoggingResponse()


def terminate_session_api_v1_logging_sessions__session_id__delete(
    session_id: str, authorization: Optional[str] = None, api_config_override: Optional[APIConfig] = None
) -> LoggingResponse:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f"/api/v1/logging/sessions/{session_id}"
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

    if response.status_code != 200:
        raise HTTPException(response.status_code, f" failed with status code: {response.status_code}")

    return LoggingResponse(**response.json()) if response.json() is not None else LoggingResponse()


def get_session_logs_api_v1_logging_sessions__session_id__logs_get(
    session_id: str,
    count: Optional[int] = None,
    authorization: Optional[str] = None,
    api_config_override: Optional[APIConfig] = None,
) -> SuccessResponse:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f"/api/v1/logging/sessions/{session_id}/logs"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Bearer { api_config.get_access_token() }",
        **({"authorization": authorization} if authorization is not None else {}),
    }
    query_params: Dict[str, Any] = {"count": count}

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


def get_logging_stats_api_v1_logging_stats_get(api_config_override: Optional[APIConfig] = None) -> SuccessResponse:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f"/api/v1/logging/stats"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Bearer { api_config.get_access_token() }",
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
