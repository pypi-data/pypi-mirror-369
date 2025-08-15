# src/hh_api/auth/models.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional
from urllib.parse import urlencode
from datetime import datetime


@dataclass(frozen=True)
class TokenPair:
    """
    Универсальная структура для токенов OAuth под JSON-ответ вида:
    {
      "access_token": "...",
      "expires_in": 1209600,
      "expires_at": "2022-12-31T23:59:59+00:00",
      "refresh_token": "..."
    }
    """
    access_token: Optional[str] = None
    expires_in: Optional[int] = 3600
    expires_at: Optional[datetime] = None
    refresh_token: Optional[str] = None



@dataclass(frozen=True)
class OAuthConfig:
    """
    Конфигурация OAuth для интеграции с hh.ru.
    По умолчанию:
      - authorize_url: https://hh.ru/oauth/authorize
      - token_url:     https://hh.ru/oauth/token
    """
    client_id: str
    client_secret: str
    redirect_uri: str
    authorize_url: str = "https://hh.ru/oauth/authorize"
    token_url: str = "https://hh.ru/oauth/token"

    # Опционально: state можно задавать здесь или при формировании URL
    state: Optional[str] = None

    def build_authorization_url(
        self,
        *,
        state: Optional[str] = None,
        redirect_uri: Optional[str] = None,
    ) -> str:
        """
        Собрать URL для Authorization Code Flow.
        :param state:        CSRF/состояние; если None — возьмём self.state.
        :param redirect_uri: Перекрыть redirect_uri; если None — self.redirect_uri.
        """
        params = {
            "response_type": "code",
            "client_id": self.client_id,
            "redirect_uri": redirect_uri or self.redirect_uri,
        }
        if state or self.state:
            params["state"] = state or self.state  # type: ignore[assignment]
        return f"{self.authorize_url}?{urlencode(params)}"


__all__ = ["TokenPair", "OAuthConfig"]
