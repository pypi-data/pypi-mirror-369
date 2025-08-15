import time, json, base64, requests
from .exceptions import ApiError

def _retryable_status(status: int) -> bool:
    return status in (429, 500, 502, 503, 504)

def request(method, url, headers=None, params=None, json_body=None, timeout=30, retries=2):
    for attempt in range(retries + 1):
        resp = requests.request(method, url, headers=headers, params=params, json=json_body, timeout=timeout)
        if resp.ok:
            try:
                return resp.json()
            except ValueError:
                return {"raw": resp.text}
        if attempt < retries and _retryable_status(resp.status_code):
            time.sleep(1.5 * (attempt + 1))
            continue
        # surface error payload for debugging
        try: payload = resp.json()
        except ValueError: payload = {"raw": resp.text}
        raise ApiError(resp.status_code, payload)
