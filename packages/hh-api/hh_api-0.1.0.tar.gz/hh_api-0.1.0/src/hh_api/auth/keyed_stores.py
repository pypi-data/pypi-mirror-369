# src/hh_api/auth/keyed_stores.py
from __future__ import annotations

import asyncio
import json
from dataclasses import asdict
from pathlib import Path
from typing import Protocol, runtime_checkable, TypeVar, Generic, Optional, Dict, Any, Union

# ВАЖНО:
# - Библиотека НЕ создаёт подключение к Redis сама.
# - Пользователь передаёт готовый инстанс redis.asyncio.Redis (из пакета redis>=5).
try:
    from redis.asyncio import Redis  # type: ignore
except Exception:  # мягкая опциональная зависимость
    Redis = Any = object  # type: ignore[assignment]  # noqa: N816

from .models import TokenPair
from .utils import parse_dt_aware, to_dt_aware


SubjectT = TypeVar("SubjectT", str, int)


@runtime_checkable
class KeyedTokenStore(Protocol, Generic[SubjectT]):
    """
    Универсальный интерфейс key-aware хранилища токенов (multi-tenant).
    Один subject (например, tg_user_id) -> одна TokenPair.

    Требования к реализациям:
    - get_tokens() возвращает None, если записи нет или она невалидна.
    - set_tokens() перезаписывает пару атомарно (в рамках одной операции хранилища).
    """
    async def get_tokens(self, subject: SubjectT) -> Optional[TokenPair]:
        ...

    async def set_tokens(self, subject: SubjectT, tokens: TokenPair) -> None:
        ...


# ======================================================================
# In-memory (для тестов/локалки)
# ======================================================================
class InMemoryKeyedTokenStore(KeyedTokenStore[SubjectT]):
    """
    Простейшее процессное хранилище.
    Подходит для тестов, локальной отладки и сценариев без межпроцессного доступа.
    """
    def __init__(self) -> None:
        self._data: Dict[Union[str, int], TokenPair] = {}
        self._lock = asyncio.Lock()  # защищаемся от гонок в рамках одного процесса

    async def get_tokens(self, subject: SubjectT) -> Optional[TokenPair]:
        async with self._lock:
            return self._data.get(subject)

    async def set_tokens(self, subject: SubjectT, tokens: TokenPair) -> None:
        async with self._lock:
            self._data[subject] = tokens


# ======================================================================
# JSON-каталог по файлу на subject (CLI/desktop/dev)
# ======================================================================
class JSONDirTokenStore(KeyedTokenStore[SubjectT]):
    """
    Хранит пары в отдельных файлах: <dir>/<subject>.json.

    Формат JSON (минимально совместимый):
    {
      "access_token": "...",
      "refresh_token": "...",
      "expires_in": 123456,                       # опционально
      "expires_at": "2025-08-13T11:22:33+00:00"   # опционально, ISO8601 (aware)
    }
    """
    def __init__(self, directory: str | Path) -> None:
        self.dir = Path(directory)
        self.dir.mkdir(parents=True, exist_ok=True)

    def _path(self, subject: SubjectT) -> Path:
        # Преобразуем subject в безопасное имя файла (int/str норм)
        return self.dir / f"{subject}.json"

    async def get_tokens(self, subject: SubjectT) -> Optional[TokenPair]:
        p = self._path(subject)
        if not p.exists():
            return None
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            return None
        # поддерживаем оба варианта: expires_at (приоритет) или expires_in
        expires_at = parse_dt_aware(data.get("expires_at"))
        return TokenPair(
            access_token=data.get("access_token"),
            refresh_token=data.get("refresh_token"),
            expires_in=data.get("expires_in"),
            expires_at=expires_at,
        )

    async def set_tokens(self, subject: SubjectT, tokens: TokenPair) -> None:
        payload: Dict[str, Any] = asdict(tokens)
        # нормализуем expires_at к ISO8601 (UTC aware) для переносимости
        if tokens.expires_at is not None:
            payload["expires_at"] = to_dt_aware(tokens.expires_at).isoformat()
        self._path(subject).write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


# ======================================================================
# Redis (per-subject ключ; JSON payload; опциональный TTL)
# ======================================================================
class RedisKeyedTokenStore(KeyedTokenStore[SubjectT]):
    """
    Redis-хранилище для multi-tenant сценариев.

    Дизайн-решения:
    - Библиотека НЕ управляет подключением: вы передаёте готовый redis.asyncio.Redis.
    - Каждая пара хранится в отдельном ключе: key = f"{prefix}:{subject}".
    - Содержимое — JSON-строка с полями TokenPair. Дата 'expires_at' хранится в ISO8601 (UTC).
    - TTL опционален и используется ТОЛЬКО для кэш-эвикции (housekeeping). Логику истечения access-токена
      определяет ваш код по полю 'expires_at'. Иначе легко потерять refresh_token.
    - Код не накладывает decode_responses=True. Если ваш Redis настроен на bytes, мы декодируем сами.
    """
    def __init__(
        self,
        client: "Redis",
        *,
        prefix: str = "hh:tokens",
        ttl_seconds: Optional[int] = None,  # если задан — вызываем EXPIRE для ключа после записи
    ) -> None:
        # Небольшая рантайм-проверка: пользователь реально передал Redis
        if not hasattr(client, "get") or not hasattr(client, "set"):
            raise TypeError("client должен быть инстансом redis.asyncio.Redis")
        self.client: "Redis" = client
        self.prefix = prefix.rstrip(":")
        self.ttl_seconds = ttl_seconds

    def _key(self, subject: SubjectT) -> str:
        # Нормализуем subject в str, чтобы ключи были единообразны
        return f"{self.prefix}:{subject}"

    @staticmethod
    def _loads(raw: Any) -> Optional[Dict[str, Any]]:
        if raw is None:
            return None
        if isinstance(raw, bytes):
            raw = raw.decode("utf-8", errors="replace")
        if not isinstance(raw, str):
            return None
        try:
            return json.loads(raw)
        except Exception:
            return None

    async def get_tokens(self, subject: SubjectT) -> Optional[TokenPair]:
        raw = await self.client.get(self._key(subject))
        data = self._loads(raw)
        if not data:
            return None
        return TokenPair(
            access_token=data.get("access_token"),
            refresh_token=data.get("refresh_token"),
            expires_in=data.get("expires_in"),
            expires_at=parse_dt_aware(data.get("expires_at")),
        )

    async def set_tokens(self, subject: SubjectT, tokens: TokenPair) -> None:
        payload = {
            "access_token": tokens.access_token,
            "refresh_token": tokens.refresh_token,
            "expires_in": tokens.expires_in,
            "expires_at": tokens.expires_at and to_dt_aware(tokens.expires_at).isoformat(),
        }
        key = self._key(subject)

        # Атомарность на уровне одной команды: сначала SET, затем при необходимости EXPIRE
        # (это две операции; если требуется строго атомарно, можно использовать lua-скрипт/PIPELINE)
        await self.client.set(key, json.dumps(payload, ensure_ascii=False))
        if self.ttl_seconds and self.ttl_seconds > 0:
            # TTL — только для авто-очистки мусора. Не равняем TTL с expires_in:
            # refresh_token может жить дольше, чем access_token.
            await self.client.expire(key, int(self.ttl_seconds))
