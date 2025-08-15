class AuthorizationRequired(Exception):
    """
    Нет токенов вообще или refresh_token отсутствует/истёк/недействителен.
    Содержит ссылку для авторизации (auth_url).
    """
    def __init__(self, auth_url: str, message: str | None = None):
        self.auth_url = auth_url
        super().__init__(message or "Authorization required. Open the URL to authorize on hh.ru.")


class AuthRefreshError(Exception):
    """Ошибка при обновлении access_token по refresh_token."""
    pass


class AuthCodeExchangeError(Exception):
    """Ошибка при обмене authorization code на токены."""
    pass


__all__ = ["AuthorizationRequired", "AuthRefreshError", "AuthCodeExchangeError"]
