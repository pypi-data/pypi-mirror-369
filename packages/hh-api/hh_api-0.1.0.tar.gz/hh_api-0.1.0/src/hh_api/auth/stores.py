# src/hh_api/auth/stores.py
from __future__ import annotations

import asyncio
import json
import os
from pathlib import Path
from typing import Optional, Protocol, runtime_checkable, Callable, Awaitable

from .models import TokenPair
from .utils import parse_dt_aware, to_dt_aware


def _decode(b: Optional[bytes | str]) -> Optional[str]:
    """Декодер для redis bytes -> str."""
    if isinstance(b, bytes):
        return b.decode()
    return b


@runtime_checkable
class TokenStore(Protocol):
    """
    Single-tenant интерфейс (совместимость с текущим кодом).
    В multi-tenant проектах используй KeyedTokenStore из keyed_stores.py.
    """
    async def get_tokens(self) -> Optional[TokenPair]: ...
    async def set_tokens(self, tokens: TokenPair) -> None: ...


class InMemoryTokenStore:
    """Память процесса. Отлично для тестов/локалки."""
    def __init__(self, tokens: Optional[TokenPair] = None):
        self._tokens = tokens
        self._lock = asyncio.Lock()

    async def get_tokens(self) -> Optional[TokenPair]:
        async with self._lock:
            return self._tokens

    async def set_tokens(self, tokens: TokenPair) -> None:
        async with self._lock:
            self._tokens = tokens


class EnvTokenStore:
    """
    Хранилище в переменных окружения (read-only по умолчанию).
    Поддерживаем:
      HH_ACCESS_TOKEN, HH_REFRESH_TOKEN, HH_EXPIRES_AT(ISO/UNIX) | HH_EXPIRES_IN(sec)
    """
    def __init__(self, *, allow_write: bool = False) -> None:
        self.allow_write = allow_write

    async def get_tokens(self) -> Optional[TokenPair]:
        acc = os.getenv("HH_ACCESS_TOKEN")
        ref = os.getenv("HH_REFRESH_TOKEN")
        if not acc and not ref:
            return None

        expires_at = parse_dt_aware(os.getenv("HH_EXPIRES_AT"))
        expires_in = None
        if expires_at is None:
            try:
                expires_in_env = os.getenv("HH_EXPIRES_IN")
                expires_in = int(expires_in_env) if expires_in_env else None
            except Exception:
                expires_in = None

        return TokenPair(
            access_token=acc,
            refresh_token=ref,
            expires_in=expires_in,
            expires_at=expires_at,
        )

    async def set_tokens(self, tokens: TokenPair) -> None:
        if not self.allow_write:
            return  # по умолчанию игнорируем запись
        if tokens.access_token:
            os.environ["HH_ACCESS_TOKEN"] = tokens.access_token
        if tokens.refresh_token:
            os.environ["HH_REFRESH_TOKEN"] = tokens.refresh_token
        if tokens.expires_at:
            os.environ["HH_EXPIRES_AT"] = to_dt_aware(tokens.expires_at).isoformat()
        elif tokens.expires_in:
            os.environ["HH_EXPIRES_IN"] = str(tokens.expires_in)


class JSONFileTokenStore:
    """
    JSON-файл (single-tenant).
    Формат:
    {
      "access_token": "...",
      "refresh_token": "...",
      "expires_in": 12345,
      "expires_at": "2025-08-13T11:22:33.123456+00:00"  # опционально
    }
    """
    def __init__(self, path: os.PathLike[str] | str):
        self.path = Path(path)

    async def get_tokens(self) -> Optional[TokenPair]:
        if not self.path.exists():
            return None
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
        except Exception:
            return None
        return TokenPair(
            access_token=data.get("access_token"),
            refresh_token=data.get("refresh_token"),
            expires_in=data.get("expires_in"),
            expires_at=parse_dt_aware(data.get("expires_at")),
        )

    async def set_tokens(self, tokens: TokenPair) -> None:
        payload = {
            "access_token": tokens.access_token,
            "refresh_token": tokens.refresh_token,
            "expires_in": tokens.expires_in,
            "expires_at": tokens.expires_at and to_dt_aware(tokens.expires_at).isoformat(),
        }
        self.path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


class RedisTokenStore:
    """
    Redis single-tenant.
    По умолчанию хранит JSON в ключе <prefix>.
    """
    def __init__(self, client: "Any", key: str = "hh:token") -> None:
        # client — redis.asyncio.Redis (redis>=5.x)
        self.client = client
        self.key = key

    async def get_tokens(self) -> Optional[TokenPair]:
        raw = await self.client.get(self.key)
        if not raw:
            return None
        try:
            data = json.loads(_decode(raw) or "")
        except Exception:
            return None
        return TokenPair(
            access_token=data.get("access_token"),
            refresh_token=data.get("refresh_token"),
            expires_in=data.get("expires_in"),
            expires_at=parse_dt_aware(data.get("expires_at")),
        )

    async def set_tokens(self, tokens: TokenPair) -> None:
        payload = {
            "access_token": tokens.access_token,
            "refresh_token": tokens.refresh_token,
            "expires_in": tokens.expires_in,
            "expires_at": tokens.expires_at and to_dt_aware(tokens.expires_at).isoformat(),
        }
        await self.client.set(self.key, json.dumps(payload, ensure_ascii=False))


class CallableTokenStore:
    """
    Адаптер к любому внешнему хранилищу/ORM.

    Пример:
      async def load() -> Optional[TokenPair]: ...
      async def save(tp: TokenPair) -> None: ...
      store = CallableTokenStore(getter=load, setter=save)
    """
    def __init__(
        self,
        getter: Callable[[], Awaitable[Optional[TokenPair]]],
        setter: Optional[Callable[[TokenPair], Awaitable[None]]] = None,
    ):
        self._getter = getter
        self._setter = setter

    async def get_tokens(self) -> Optional[TokenPair]:
        return await self._getter()

    async def set_tokens(self, tokens: TokenPair) -> None:
        if self._setter is not None:
            await self._setter(tokens)


__all__ = [
    "TokenStore",
    "InMemoryTokenStore",
    "EnvTokenStore",
    "JSONFileTokenStore",
    "RedisTokenStore",
    "CallableTokenStore",
]
