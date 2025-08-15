import json
from typing import *

import httpx

from ..api_config import APIConfig, HTTPException
from ..models import *


def broadcast_message_api_v1_admin_broadcast_post(
    data: BroadcastMessageRequest,
    authorization: Optional[str] = None,
    api_config_override: Optional[APIConfig] = None,
) -> BroadcastResultResponse:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f"/api/v1/admin/broadcast"
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

    return BroadcastResultResponse(**response.json()) if response.json() is not None else BroadcastResultResponse()


def manage_maintenance_mode_api_v1_admin_maintenance_post(
    data: MaintenanceModeRequest,
    authorization: Optional[str] = None,
    api_config_override: Optional[APIConfig] = None,
) -> MaintenanceStatusResponse:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f"/api/v1/admin/maintenance"
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

    return MaintenanceStatusResponse(**response.json()) if response.json() is not None else MaintenanceStatusResponse()


def get_maintenance_status_api_v1_admin_maintenance_status_get(
    authorization: Optional[str] = None, api_config_override: Optional[APIConfig] = None
) -> MaintenanceStatusResponse:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f"/api/v1/admin/maintenance/status"
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

    return MaintenanceStatusResponse(**response.json()) if response.json() is not None else MaintenanceStatusResponse()


def get_admin_service_stats_api_v1_admin_stats_get(
    authorization: Optional[str] = None, api_config_override: Optional[APIConfig] = None
) -> ServiceStatsResponse:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f"/api/v1/admin/stats"
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

    return ServiceStatsResponse(**response.json()) if response.json() is not None else ServiceStatsResponse()
