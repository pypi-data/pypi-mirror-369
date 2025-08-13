# src/hh_api/auth/token_manager.py
from __future__ import annotations

import asyncio
import random
from typing import Optional, Dict, Any, Generic, TypeVar

try:
    import httpx
except Exception:
    httpx = None  # позволяем импорт без httpx (юнит-тесты)

from .models import TokenPair, OAuthConfig
from .keyed_stores import KeyedTokenStore
from .locks import LockProvider, InProcessLockProvider
from .utils import now_utc, is_expired

SubjectT = TypeVar("SubjectT", str, int)


class RetryPolicy:
    """
    Простая политика ретраев: 429 и 5xx — ретраим с экспоненциальной паузой.
    """
    def __init__(self, attempts: int = 3, base_delay: float = 0.5, max_delay: float = 4.0) -> None:
        self.attempts = attempts
        self.base_delay = base_delay
        self.max_delay = max_delay

    async def sleep(self, attempt: int) -> None:
        delay = min(self.max_delay, self.base_delay * (2 ** (attempt - 1)))
        # добавим джиттер
        await asyncio.sleep(delay * (0.7 + random.random() * 0.6))


class TokenManager(Generic[SubjectT]):
    """
    Универсальный менеджер токенов под multi-tenant сценарий.

    Публичный API:
      - authorization_url(subject, state?) -> str
      - exchange_code(subject, code) -> TokenPair
      - ensure_access(subject) -> str (вернёт валидный access_token; при необходимости обновит)
      - refresh(subject, refresh_token?) -> TokenPair
      - get_auth_header(access_token) -> dict
    """
    def __init__(
        self,
        config: OAuthConfig,
        store: KeyedTokenStore[SubjectT],
        *,
        user_agent: str,
        http_client: Optional["httpx.AsyncClient"] = None,
        retry: Optional[RetryPolicy] = None,
        lock_provider: Optional[LockProvider[SubjectT]] = None,
    ) -> None:
        self.config = config
        self.store = store
        self.user_agent = user_agent
        self.client = http_client or (httpx and httpx.AsyncClient(timeout=20.0))
        self._close_client = http_client is None
        self.retry = retry or RetryPolicy()
        self.locks = lock_provider or InProcessLockProvider()

        if self.client is None:
            raise RuntimeError("httpx не доступен. Установите пакет 'httpx'.")

    async def aclose(self) -> None:
        if self._close_client and self.client is not None:
            await self.client.aclose()

    # ---------------------------
    # Публичный API
    # ---------------------------
    def authorization_url(self, subject: SubjectT, state: Optional[str] = None) -> str:
        return self.config.build_authorization_url(state=state)

    async def exchange_code(self, subject: SubjectT, code: str) -> TokenPair:
        data = {
            "grant_type": "authorization_code",
            "client_id": self.config.client_id,
            "client_secret": self.config.client_secret,
            "code": code,
        }
        headers = {"User-Agent": self.user_agent}
        resp = await self._post_with_retry(self.config.token_url, data=data, headers=headers)
        payload = resp.json()
        tokens = self._tokenpair_from_payload(payload)
        await self.store.set_tokens(subject, tokens)
        return tokens

    async def ensure_access(self, subject: SubjectT) -> str:
        """
        Вернуть действующий access_token (авто-рефреш при необходимости).
        Если нет токенов/refresh — вызывающему нужно отправить пользователя на authorization_url().
        """
        tokens = await self.store.get_tokens(subject)
        if not tokens or not tokens.refresh_token:
            raise RuntimeError("Нет токенов. Отправьте пользователя на authorization_url().")

        if tokens.access_token and not is_expired(tokens.expires_at, skew_seconds=30):
            return tokens.access_token

        # защитимся от гонки рефреша
        async with self.locks.acquire(subject):
            tokens = await self.store.get_tokens(subject) or tokens
            if tokens.access_token and not is_expired(tokens.expires_at, skew_seconds=30):
                return tokens.access_token
            tokens = await self.refresh(subject, tokens.refresh_token)
            return tokens.access_token or ""

    async def refresh(self, subject: SubjectT, refresh_token: Optional[str] = None) -> TokenPair:
        existing = await self.store.get_tokens(subject)
        rt = refresh_token or (existing and existing.refresh_token)
        if not rt:
            raise RuntimeError("Нет refresh_token — требуется повторная авторизация.")

        data = {
            "grant_type": "refresh_token",
            "client_id": self.config.client_id,
            "client_secret": self.config.client_secret,
            "refresh_token": rt,
        }
        headers = {"User-Agent": self.user_agent}
        resp = await self._post_with_retry(self.config.token_url, data=data, headers=headers)
        payload = resp.json()

        new_tokens = self._tokenpair_from_payload(payload, fallback_refresh=rt)
        await self.store.set_tokens(subject, new_tokens)
        return new_tokens

    def get_auth_header(self, access_token: str) -> Dict[str, str]:
        return {"Authorization": f"Bearer {access_token}", "User-Agent": self.user_agent}

    # ---------------------------
    # Вспомогательные
    # ---------------------------
    async def _post_with_retry(self, url: str, *, data: Dict[str, Any], headers: Dict[str, str]):
        assert self.client is not None
        last_exc: Optional[Exception] = None
        for attempt in range(1, self.retry.attempts + 1):
            try:
                resp = await self.client.post(url, data=data, headers=headers)
                # Ретраим 429 и 5xx
                if resp.status_code == 429 or 500 <= resp.status_code < 600:
                    last_exc = httpx.HTTPStatusError(f"status={resp.status_code}", request=resp.request, response=resp)
                    await self.retry.sleep(attempt)
                    continue
                resp.raise_for_status()
                return resp
            except (httpx.RequestError, httpx.HTTPStatusError) as e:
                last_exc = e
                # 4xx (кроме 429) ретраить бессмысленно
                if isinstance(e, httpx.HTTPStatusError) and not (
                    e.response is not None and (e.response.status_code == 429 or 500 <= e.response.status_code < 600)
                ):
                    break
                await self.retry.sleep(attempt)
        if last_exc:
            raise last_exc
        raise RuntimeError("Неизвестная ошибка запроса.")

    @staticmethod
    def _tokenpair_from_payload(payload: Dict[str, Any], *, fallback_refresh: Optional[str] = None) -> TokenPair:
        access = payload.get("access_token")
        if not access:
            raise RuntimeError("В ответе нет access_token.")
        refresh = payload.get("refresh_token") or fallback_refresh
        expires_in = int(payload.get("expires_in", 0)) or None
        expires_at = None
        if expires_in:
            expires_at = now_utc() + __import__("datetime").timedelta(seconds=expires_in)
        return TokenPair(
            access_token=access,
            refresh_token=refresh,
            expires_in=expires_in,
            expires_at=expires_at,
        )
