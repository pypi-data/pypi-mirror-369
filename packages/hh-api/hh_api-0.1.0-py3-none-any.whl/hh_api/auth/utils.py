# src/hh_api/auth/utils.py
from __future__ import annotations
import datetime as dt
from typing import Optional


def now_utc() -> dt.datetime:
    """Текущее время в UTC (aware)."""
    return dt.datetime.now(dt.UTC)


def is_expired(
    expires_at: Optional[dt.datetime],
    skew_sec: int = 0,              # старое имя параметра (совместимость)
    *,
    skew_seconds: Optional[int] = None,  # новое имя, если вызывают как named arg
) -> bool:
    """
    True, если токен истёк или не задан.
    Используем защитный сдвиг (clock skew).
    Приоритет: skew_seconds (если передан), иначе skew_sec.
    """
    if not expires_at:
        return True
    skew = skew_seconds if skew_seconds is not None else skew_sec
    return expires_at <= (now_utc() + dt.timedelta(seconds=max(0, int(skew))))


def parse_dt_aware(value: Optional[str | int | float]) -> Optional[dt.datetime]:
    """
    Парсинг даты в aware-дату (UTC):
    - ISO8601: '2025-08-13T12:34:56.123456+00:00' (или 'Z')
    - UNIX seconds: int/float
    """
    if value is None:
        return None
    if isinstance(value, str):
        try:
            v = value
            if v.endswith("Z"):
                v = v[:-1] + "+00:00"
            d = dt.datetime.fromisoformat(v)
            if d.tzinfo is None:
                d = d.replace(tzinfo=dt.UTC)
            return d.astimezone(dt.UTC)
        except Exception:
            try:
                value = int(value)
            except Exception:
                return None
    if isinstance(value, (int, float)):
        return dt.datetime.fromtimestamp(int(value), tz=dt.UTC)
    return None


def to_dt_aware(value: dt.datetime) -> dt.datetime:
    """Гарантирует aware (UTC) datetime."""
    if value.tzinfo is None:
        return value.replace(tzinfo=dt.UTC)
    return value.astimezone(dt.UTC)


__all__ = ["now_utc", "is_expired", "parse_dt_aware", "to_dt_aware"]
