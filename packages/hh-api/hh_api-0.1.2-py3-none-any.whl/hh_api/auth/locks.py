# src/hh_api/auth/locks.py
from __future__ import annotations
import asyncio
from typing import Protocol, TypeVar, Generic, Dict, Union, AsyncIterator
from contextlib import asynccontextmanager

SubjectT = TypeVar("SubjectT", str, int)


class LockProvider(Protocol, Generic[SubjectT]):
    """
    Интерфейс провайдера замков (per-subject), чтобы несколько корутин
    не делали refresh одновременно.
    """
    @asynccontextmanager
    async def acquire(self, subject: SubjectT) -> AsyncIterator[None]: ...


class InProcessLockProvider(LockProvider[SubjectT]):
    """
    Простая in-process реализация.
    Для мультипроцесс/кластера можно сделать RedisLockProvider.
    """
    def __init__(self) -> None:
        self._locks: Dict[Union[str, int], asyncio.Lock] = {}

    async def _get_lock(self, subject: SubjectT) -> asyncio.Lock:
        lock = self._locks.get(subject)
        if lock is None:
            lock = asyncio.Lock()
            self._locks[subject] = lock
        return lock

    @asynccontextmanager
    async def acquire(self, subject: SubjectT):
        lock = await self._get_lock(subject)
        await lock.acquire()
        try:
            yield
        finally:
            lock.release()
