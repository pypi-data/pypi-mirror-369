class GavaconnectError(Exception): ...
class AuthError(GavaconnectError): ...
class ApiError(GavaconnectError):
    def __init__(self, status, payload):
        super().__init__(f"API error {status}")
        self.status = status
        self.payload = payload
