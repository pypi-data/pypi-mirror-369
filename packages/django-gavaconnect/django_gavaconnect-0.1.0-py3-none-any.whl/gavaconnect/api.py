from .conf import ENV, SANDBOX, PRODUCTION, ENDPOINTS
from .auth import get_token
from .http import request

def _base_url():
    return (SANDBOX if ENV == "sandbox" else PRODUCTION).BASE_URL.rstrip("/")

def _auth_headers():
    return {"Authorization": f"Bearer {get_token()}"}

def pin_by_pin(pin: str):
    url = _base_url() + ENDPOINTS["pin_by_pin"]
    return request("POST", url, headers=_auth_headers(), json_body={"pin": pin})

def pin_by_id(id_number: str, taxpayer_type: str):
    # taxpayer_type example values: "KE" / "NKE" / "NKENR" / "COMP" — confirm in portal.
    url = _base_url() + ENDPOINTS["pin_by_id"]
    return request("POST", url, headers=_auth_headers(),
                   json_body={"idNumber": id_number, "taxpayerType": taxpayer_type})

def it_exemption(pin: str | None = None, certificate_no: str | None = None):
    # KRA doc shows an IT Exemption checker endpoint; payload shape may vary 
    url = _base_url() + ENDPOINTS["it_exemption"]
    body = {"pin": pin} if pin else {"certificateNumber": certificate_no}
    return request("POST", url, headers=_auth_headers(), json_body=body)

def vat_exemption(pin: str | None = None, certificate_no: str | None = None):
    """
    Calls VAT Exemption checker endpoint.
    Provide either `pin` or `certificate_no`.
    """
    url = _base_url() + ENDPOINTS["vat_exemption"]
    body = {"pin": pin} if pin else {"certificateNumber": certificate_no}
    return request("POST", url, headers=_auth_headers(), json_body=body)

def prn_search(prn: str):
    url = _base_url() + ENDPOINTS["prn_search"]
    return request("POST", url, headers=_auth_headers(), json_body={"prn": prn})

