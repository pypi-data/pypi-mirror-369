import base64, time, requests
from django.core.cache import cache
from .conf import CLIENT_ID, CLIENT_SECRET, SANDBOX, PRODUCTION, ENV
from .exceptions import AuthError

CFG = SANDBOX if ENV == "sandbox" else PRODUCTION
CACHE_KEY = f"gavaconnect:token:{ENV}"

def _basic_header() -> str:
    if not CLIENT_ID or not CLIENT_SECRET:
        raise AuthError("Missing GAVACONNECT_CLIENT_ID/CLIENT_SECRET")
    creds = f"{CLIENT_ID}:{CLIENT_SECRET}".encode()
    return "Basic " + base64.b64encode(creds).decode()

def _fetch_token() -> tuple[str, int]:
    headers = {"Authorization": _basic_header()}
    if CFG.TOKEN_METHOD.upper() == "GET":
        resp = requests.get(CFG.TOKEN_URL, headers=headers, timeout=20)
    else:
        resp = requests.post(CFG.TOKEN_URL, headers=headers, data={"grant_type": "client_credentials"}, timeout=20)
    if resp.status_code != 200:
        raise AuthError(f"Token fetch failed: {resp.status_code} {resp.text}")
    data = resp.json()
    access_token = data.get("access_token") or data.get("token")  # accommodate variations
    expires_in = int(data.get("expires_in", 3600))
    if not access_token:
        raise AuthError(f"Token payload missing access_token: {data}")
    return access_token, expires_in

def get_token() -> str:
    cached = cache.get(CACHE_KEY)
    if cached:
        return cached
    token, ttl = _fetch_token()
    # Save with safety buffer (minus 60s)
    cache.set(CACHE_KEY, token, max(60, ttl - 60))
    return token
