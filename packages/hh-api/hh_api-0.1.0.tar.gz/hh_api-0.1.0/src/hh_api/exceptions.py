# =========================
# Exceptions
# =========================

class AuthorizationRequired(Exception):
    """
    Бросается, когда в хранилище нет токенов.
    Внутри хранит ссылку для авторизации (auth_url).
    """

    def __init__(self, auth_url: str, message: str | None = None):
        self.auth_url = auth_url
        super().__init__(message or "Authorization required. Open the URL to authorize on hh.ru.")







class HHAPIError(Exception):
    def __init__(self, status_code: int, message: str):
        super().__init__(f"HH API error {status_code}: {message}")
        self.status_code = status_code
        self.message = message

class HHAuthError(HHAPIError):
    pass

class HHNetworkError(Exception):
    pass
