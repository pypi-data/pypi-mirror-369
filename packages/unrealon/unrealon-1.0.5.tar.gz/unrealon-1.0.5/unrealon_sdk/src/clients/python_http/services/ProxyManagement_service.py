import json
from typing import *

import httpx

from ..api_config import APIConfig, HTTPException
from ..models import *


def list_proxies_api_v1_proxies__get(
    status: Optional[Union[ProxyStatus]] = None,
    country: Optional[str] = None,
    provider: Optional[Union[ProxyProvider]] = None,
    healthy_only: Optional[bool] = None,
    skip: Optional[int] = None,
    limit: Optional[int] = None,
    authorization: Optional[str] = None,
    api_config_override: Optional[APIConfig] = None,
) -> ProxyListResponse:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f"/api/v1/proxies/"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Bearer { api_config.get_access_token() }",
        **({"authorization": authorization} if authorization is not None else {}),
    }
    query_params: Dict[str, Any] = {
        "status": status,
        "country": country,
        "provider": provider,
        "healthy_only": healthy_only,
        "skip": skip,
        "limit": limit,
    }

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

    return ProxyListResponse(**response.json()) if response.json() is not None else ProxyListResponse()


def cleanup_expired_proxies_api_v1_proxies_maintenance_cleanup_post(
    authorization: Optional[str] = None, api_config_override: Optional[APIConfig] = None
) -> SuccessResponse:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f"/api/v1/proxies/maintenance/cleanup"
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
            "post",
            httpx.URL(path),
            headers=headers,
            params=query_params,
        )

    if response.status_code != 200:
        raise HTTPException(response.status_code, f" failed with status code: {response.status_code}")

    return SuccessResponse(**response.json()) if response.json() is not None else SuccessResponse()


def sync_proxies_api_v1_proxies_maintenance_sync_get(
    authorization: Optional[str] = None, api_config_override: Optional[APIConfig] = None
) -> SuccessResponse:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f"/api/v1/proxies/maintenance/sync"
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


def purchase_proxies_api_v1_proxies_procurement_purchase_post(
    data: ProxyPurchaseRequest,
    authorization: Optional[str] = None,
    api_config_override: Optional[APIConfig] = None,
) -> SuccessResponse:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f"/api/v1/proxies/procurement/purchase"
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

    return SuccessResponse(**response.json()) if response.json() is not None else SuccessResponse()


def report_blocked_proxy_api_v1_proxies_rotation_block_post(
    data: ProxyBlockRequest,
    authorization: Optional[str] = None,
    api_config_override: Optional[APIConfig] = None,
) -> SuccessResponse:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f"/api/v1/proxies/rotation/block"
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

    return SuccessResponse(**response.json()) if response.json() is not None else SuccessResponse()


def request_proxy_rotation_api_v1_proxies_rotation_request_post(
    data: ProxyRotationRequest,
    authorization: Optional[str] = None,
    api_config_override: Optional[APIConfig] = None,
) -> SuccessResponse:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f"/api/v1/proxies/rotation/request"
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

    return SuccessResponse(**response.json()) if response.json() is not None else SuccessResponse()


def get_proxy_statistics_api_v1_proxies_statistics_get(
    authorization: Optional[str] = None, api_config_override: Optional[APIConfig] = None
) -> Dict[str, Any]:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f"/api/v1/proxies/statistics"
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

    return response.json()


def get_proxy_details_api_v1_proxies__proxy_id__get(
    proxy_id: str, authorization: Optional[str] = None, api_config_override: Optional[APIConfig] = None
) -> SuccessResponse:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f"/api/v1/proxies/{proxy_id}"
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


def record_proxy_usage_api_v1_proxies__proxy_id__usage_post(
    proxy_id: str,
    data: ProxyUsageRequest,
    authorization: Optional[str] = None,
    api_config_override: Optional[APIConfig] = None,
) -> SuccessResponse:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f"/api/v1/proxies/{proxy_id}/usage"
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

    return SuccessResponse(**response.json()) if response.json() is not None else SuccessResponse()
