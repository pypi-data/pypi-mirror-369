# src/hh_api/auth/__init__.py
from .models import TokenPair, OAuthConfig
from .exceptions import AuthorizationRequired, AuthRefreshError, AuthCodeExchangeError
from .stores import (
    TokenStore,
    InMemoryTokenStore,
    EnvTokenStore,
    JSONFileTokenStore,
    RedisTokenStore,
    CallableTokenStore,
)
from .oauth import OAuthTokenAuth, exchange_code_for_tokens

# Новые multi-tenant инструменты
from .keyed_stores import (
    KeyedTokenStore,
    InMemoryKeyedTokenStore,
    JSONDirTokenStore,
    RedisKeyedTokenStore,
)
from .locks import LockProvider, InProcessLockProvider
from .token_manager import TokenManager, RetryPolicy

__all__ = [
    # модели/исключения
    "TokenPair",
    "OAuthConfig",
    "AuthorizationRequired",
    "AuthRefreshError",
    "AuthCodeExchangeError",
    # single-tenant стораджи
    "TokenStore",
    "InMemoryTokenStore",
    "EnvTokenStore",
    "JSONFileTokenStore",
    "RedisTokenStore",
    "CallableTokenStore",
    # single-tenant адаптер
    "OAuthTokenAuth",
    "exchange_code_for_tokens",
    # multi-tenant стораджи
    "KeyedTokenStore",
    "InMemoryKeyedTokenStore",
    "JSONDirTokenStore",
    "RedisKeyedTokenStore",
    # локи/ретраи/менеджер
    "LockProvider",
    "InProcessLockProvider",
    "TokenManager",
    "RetryPolicy",
]
