from urllib3.util.retry import Retry
from typing import Dict, Any, Optional

import requests


def post_with_retries(
    url: str,
    payload: Dict[str, Any],
    api_key: Optional[str] = None,
    timeout: int = 30,
    num_retries: int = 3,
) -> requests.Response:
    retry_strategy = Retry(
        total=num_retries,
        backoff_factor=3,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["POST"],
    )

    session = requests.Session()
    adapter = requests.adapters.HTTPAdapter(max_retries=retry_strategy)
    session.mount("https://", adapter)

    headers = {
        "x-api-key": api_key,
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    try:
        response = session.post(url, headers=headers, json=payload, timeout=timeout)
        response.raise_for_status()
        return response
    except (
        requests.exceptions.ConnectionError,
        requests.exceptions.RequestException,
        requests.exceptions.HTTPError,
    ) as e:
        print(f"Failed after {retry_strategy.total} retries: {str(e)}")
        raise


def get_with_retries(
    url: str, api_key: Optional[str] = None, timeout: int = 30, num_retries: int = 3
) -> requests.Response:
    retry_strategy = Retry(
        total=num_retries,
        backoff_factor=30,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET"],
    )

    session = requests.Session()
    adapter = requests.adapters.HTTPAdapter(max_retries=retry_strategy)
    session.mount("https://", adapter)

    headers = {}
    if api_key:
        headers["x-api-key"] = api_key
        headers["Authorization"] = f"Bearer {api_key}"

    try:
        response = session.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()
        return response
    except (
        requests.exceptions.ConnectionError,
        requests.exceptions.RequestException,
        requests.exceptions.HTTPError,
    ) as e:
        print(f"Failed after {retry_strategy.total} retries: {str(e)}")
        raise
