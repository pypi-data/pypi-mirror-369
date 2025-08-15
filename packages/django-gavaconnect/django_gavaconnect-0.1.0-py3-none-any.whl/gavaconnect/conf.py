import os
from dataclasses import dataclass

@dataclass(frozen=True)
class EnvConfig:
    BASE_URL: str
    TOKEN_URL: str
    TOKEN_METHOD: str = "GET"  # Some KRA docs show GET client_credentials
    SCOPE: str | None = None

# NOTE: Confirm these URLs in the GavaConnect portal before use.
SANDBOX = EnvConfig(
    BASE_URL=os.getenv("GAVACONNECT_SANDBOX_BASE_URL", "https://sbx.kra.go.ke"),
    TOKEN_URL=os.getenv("GAVACONNECT_SANDBOX_TOKEN_URL", "https://sbx.kra.go.ke/oauth/v1/generate?grant_type=client_credentials"),
)

PRODUCTION = EnvConfig(
    BASE_URL=os.getenv("GAVACONNECT_PROD_BASE_URL", "https://api.kra.go.ke"),
    TOKEN_URL=os.getenv("GAVACONNECT_PROD_TOKEN_URL", "https://api.kra.go.ke/oauth/v1/generate?grant_type=client_credentials"),
)

ENV = os.getenv("GAVACONNECT_ENV", "sandbox").lower()
CLIENT_ID = os.getenv("GAVACONNECT_CLIENT_ID", "")
CLIENT_SECRET = os.getenv("GAVACONNECT_CLIENT_SECRET", "")

# Endpoint paths (override in settings or env if KRA updates)
ENDPOINTS = {
    "pin_by_pin": os.getenv("GAVACONNECT_EP_PIN_BY_PIN", "/checker/v1/pinbypin"),
    "pin_by_id":  os.getenv("GAVACONNECT_EP_PIN_BY_ID",  "/checker/v1/pinbyid"),
    "it_exemption": os.getenv("GAVACONNECT_EP_IT_EXEMPT", "/checker/v1/itexemption"),
    "vat_exemption": os.getenv("GAVACONNECT_EP_VAT_EXEMPT", "/dtd/checker/v1/vatexemption"),  # Added VAT exemption
    "prn_search": os.getenv("GAVACONNECT_EP_PRN_SEARCH", "/dtd/checker/v1/prn"),
}
