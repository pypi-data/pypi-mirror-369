import json
from unittest.mock import patch
from gavaconnect import api

@patch("gavaconnect.auth.requests.get")
@patch("gavaconnect.http.requests.request")
def test_pin_by_pin(mock_req, mock_token):
    mock_token.return_value.status_code = 200
    mock_token.return_value.json.return_value = {"access_token": "t", "expires_in": 3600}
    mock_req.return_value.ok = True
    mock_req.return_value.json.return_value = {"status": "OK", "pinStatus": "VALID"}

    resp = api.pin_by_pin("A123456789B")
    assert resp["status"] == "OK"
