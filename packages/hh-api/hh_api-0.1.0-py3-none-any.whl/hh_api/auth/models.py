# src/hh_api/auth/models.py
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass, field
from typing import Optional, Iterable, Union
from urllib.parse import urlencode


@dataclass(frozen=True)
class TokenPair:
    """
    Универсальная структура для токенов OAuth.
    - Если передан expires_in, то expires_at автозаполняется (UTC-aware).
    - Если expires_at передан явно — используется он.
    """
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    expires_in: Optional[int] = 3600
    expires_at: Optional[dt.datetime] = field(default=None)

    def __post_init__(self) -> None:
        # Если срок жизни задан через expires_in, но нет expires_at — проставим.
        if self.expires_at is None and self.expires_in:
            object.__setattr__(
                self,
                "expires_at",
                dt.datetime.now(dt.UTC) + dt.timedelta(seconds=int(self.expires_in)),
            )


@dataclass(frozen=True)
class OAuthConfig:
    """
    Конфигурация OAuth для интеграции с hh.ru.
    По умолчанию:
      - authorize_url: https://hh.ru/oauth/authorize
      - token_url:     https://api.hh.ru/oauth/token
    """
    client_id: str
    client_secret: str
    redirect_uri: str
    authorize_url: str = "https://hh.ru/oauth/authorize"
    token_url: str = "https://api.hh.ru/oauth/token"

    # Опционально: scope/state можно задавать здесь или при формировании URL
    scope: Optional[Union[str, Iterable[str]]] = None
    state: Optional[str] = None

    def build_authorization_url(
        self,
        *,
        state: Optional[str] = None,
        scope: Optional[Union[str, Iterable[str]]] = None,
        redirect_uri: Optional[str] = None,
    ) -> str:
        """
        Собрать URL для Authorization Code Flow.
        :param state:        CSRF/состояние; если None — возьмём self.state.
        :param scope:        Скоуп(ы) через пробел; если None — self.scope.
        :param redirect_uri: Перекрыть redirect_uri; если None — self.redirect_uri.
        """
        scope_val = scope if scope is not None else self.scope
        scope_str = scope_val if isinstance(scope_val, str) else (" ".join(scope_val) if scope_val else "")
        params = {
            "response_type": "code",
            "client_id": self.client_id,
            "redirect_uri": redirect_uri or self.redirect_uri,
        }
        if scope_str:
            params["scope"] = scope_str
        if state or self.state:
            params["state"] = state or self.state  # type: ignore[assignment]
        return f"{self.authorize_url}?{urlencode(params)}"

    # Для обратной совместимости, если где-то вызывали старое имя:
    build_authorize_url = build_authorization_url


__all__ = ["TokenPair", "OAuthConfig"]
