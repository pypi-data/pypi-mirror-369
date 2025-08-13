# src/hh_api/auth/oauth.py
from __future__ import annotations

from typing import Optional

try:
    import httpx  # сетевые запросы к token endpoint
except Exception:
    httpx = None  # позволяем импорт модуля без httpx (юнит-тесты без сети)

from .models import TokenPair, OAuthConfig
from .stores import TokenStore
from .exceptions import AuthorizationRequired, AuthRefreshError, AuthCodeExchangeError
from .utils import is_expired


DEFAULT_USER_AGENT = "hh-api-auth/1.0"  # Обязателен User-Agent во всех запросах к hh API


class OAuthTokenAuth:
    """
    Backward-compatible single-tenant адаптер (для существующего кода).
    Логика:
      - Берём токены из store.
      - Если access жив — возвращаем.
      - Если истёк — обновляем по refresh_token.
      - Если токенов нет/нет refresh — бросаем AuthorizationRequired(auth_url).
    """
    def __init__(
        self,
        config: OAuthConfig,
        store: TokenStore,
        *,
        user_agent: str = DEFAULT_USER_AGENT,
        http_client: Optional["httpx.AsyncClient"] = None,
        skew_seconds: int = 30,  # защитный сдвиг при проверке истечения
    ) -> None:
        self.config = config
        self.store = store
        self.user_agent = user_agent
        self.client = http_client or (httpx and httpx.AsyncClient(timeout=20.0))
        self._close_after = http_client is None
        self.skew_seconds = skew_seconds

        if self.client is None:
            raise RuntimeError("httpx не доступен. Установите пакет 'httpx'.")

    async def create(self) -> TokenPair:
        """
        Главный вход: гарантированно вернуть токены.
        Может поднять AuthorizationRequired, если нужна первичная авторизация.
        """
        try:
            assert self.client is not None
            tokens = await self.store.get_tokens()

            # Нет токенов или нет refresh_token — нужна первичная авторизация пользователя.
            if not tokens or not tokens.refresh_token:
                raise AuthorizationRequired(self.config.build_authorization_url())

            # Валидный access — ок.
            if tokens.access_token and not is_expired(tokens.expires_at, skew_seconds=self.skew_seconds):
                return tokens

            # Пытаемся обновить по refresh_token
            new_tokens = await self._refresh_access_token(tokens.refresh_token)
            try:
                await self.store.set_tokens(new_tokens)
            except Exception:
                # В библиотеке не молчим — но и не рушим: пусть потребитель решает,
                # как критично падать на ошибке сохранения.
                # Здесь можно добавить logging.warning(...), если ты используешь логгер.
                pass
            return new_tokens

        finally:
            if self._close_after and self.client is not None:
                await self.client.aclose()

    async def _refresh_access_token(self, refresh_token: str) -> TokenPair:
        """
        Обновление токена по refresh_token.
        Передаём client_id и client_secret в теле (единый стиль с обменом code).
        """
        assert self.client is not None
        data = {
            "grant_type": "refresh_token",
            "client_id": self.config.client_id,
            "client_secret": self.config.client_secret,
            "refresh_token": refresh_token,
        }
        headers = {"User-Agent": self.user_agent}

        try:
            resp = await self.client.post(self.config.token_url, data=data, headers=headers)
            resp.raise_for_status()
            payload = resp.json()
        except Exception as e:
            if httpx is not None and isinstance(e, httpx.HTTPStatusError):
                raise AuthRefreshError(f"HTTP error during refresh: {e}") from e
            raise

        # Нормализация в TokenPair
        access = payload.get("access_token")
        if not access:
            raise AuthRefreshError("В ответе отсутствует access_token.")
        refresh = payload.get("refresh_token") or refresh_token
        expires_in = int(payload.get("expires_in", 0)) or None

        return TokenPair(
            access_token=access,
            refresh_token=refresh,
            expires_in=expires_in,
        )


async def exchange_code_for_tokens(
    config: OAuthConfig,
    code: str,
    *,
    user_agent: str = DEFAULT_USER_AGENT,
    http_client: Optional["httpx.AsyncClient"] = None,
) -> TokenPair:
    """
    Обмен authorization_code на access/refresh токены.
    Возвращаем TokenPair. Ошибки HTTP конвертируем в AuthCodeExchangeError.
    """
    client = http_client or (httpx and httpx.AsyncClient(timeout=20.0))
    close_after = http_client is None

    if client is None:
        raise RuntimeError("httpx не доступен. Установите пакет 'httpx'.")

    data = {
        "grant_type": "authorization_code",
        "client_id": config.client_id,
        "client_secret": config.client_secret,
        "code": code,
        # redirect_uri можно передать при необходимости конкретной настройки приложения
    }
    headers = {"User-Agent": user_agent}

    try:
        resp = await client.post(config.token_url, data=data, headers=headers)
        resp.raise_for_status()
        payload = resp.json()
        access = payload.get("access_token")
        if not access:
            raise AuthCodeExchangeError("В ответе отсутствует access_token.")
        return TokenPair(
            access_token=access,
            refresh_token=payload.get("refresh_token"),
            expires_in=int(payload.get("expires_in", 0)) or None,
        )
    except Exception as e:
        if httpx is not None and isinstance(e, httpx.HTTPStatusError):
            raise AuthCodeExchangeError(f"HTTP error during code exchange: {e}") from e
        raise
    finally:
        if close_after:
            await client.aclose()


__all__ = ["OAuthTokenAuth", "exchange_code_for_tokens"]
