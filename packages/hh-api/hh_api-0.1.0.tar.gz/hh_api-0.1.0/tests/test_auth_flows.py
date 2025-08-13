# tests/test_auth_flows.py
import time
import json
import asyncio
import pytest

from hh_api.auth import (
    OAuthTokenAuth,
    OAuthConfig,
    TokenPair,
    InMemoryTokenStore,
    JSONFileTokenStore,
    CallableTokenStore,
    AuthorizationRequired,
    AuthRefreshError,
)

# ---------- helpers: fake http client & responses ----------

class FakeResponse:
    def __init__(self, status_code=200, json_data=None, url="https://hh.ru/oauth/token"):
        self.status_code = status_code
        self._json = json_data or {}
        self._url = url

    def json(self):
        return self._json

    def raise_for_status(self):
        # Если установлен httpx — поднимем реальный HTTPStatusError
        httpx = pytest.importorskip("httpx")
        if self.status_code >= 400:
            req = httpx.Request("POST", self._url)
            resp = httpx.Response(self.status_code, request=req)
            raise httpx.HTTPStatusError(f"{self.status_code} error", request=req, response=resp)


class FakeHTTPClient:
    def __init__(self, responses):
        """
        responses: список FakeResponse, будет возвращаться по порядку на вызовы post()
        """
        self._responses = list(responses)
        self.calls = []

    async def post(self, url, data=None, headers=None, auth=None):
        self.calls.append({"url": url, "data": dict(data or {}), "headers": dict(headers or {}), "auth": auth})
        if not self._responses:
            # На всякий случай, если вызвали больше, чем ожидалось
            return FakeResponse(status_code=500, json_data={"error": "no more responses"})
        return self._responses.pop(0)

    async def aclose(self):
        return


# ---------- fixtures ----------

@pytest.fixture
def oauth():
    # clock_skew делаем побольше, чтобы удобнее было тестить порог истечения
    return OAuthConfig(
        client_id="client-id",
        client_secret=None,
        redirect_uri="https://localhost/callback",
        scope=["basic"],
        clock_skew=30,
    )


# ---------- tests: AuthorizationRequired branches ----------

@pytest.mark.asyncio
async def test_no_tokens_at_all_raises_authrequired(oauth):
    store = InMemoryTokenStore(tokens=None)
    with pytest.raises(AuthorizationRequired) as e:
        await OAuthTokenAuth.create(store, oauth)
    assert oauth.build_authorization_url() in e.value.auth_url

@pytest.mark.asyncio
async def test_missing_refresh_token_raises_authrequired(oauth):
    store = InMemoryTokenStore(TokenPair(access_token="A", refresh_token=None))
    with pytest.raises(AuthorizationRequired):
        await OAuthTokenAuth.create(store, oauth)

@pytest.mark.asyncio
async def test_expired_refresh_token_raises_authrequired(oauth):
    now = int(time.time())
    store = InMemoryTokenStore(TokenPair(
        access_token="A",
        refresh_token="R",
        refresh_expires_at_ts=now - 1,  # явная просрочка
    ))
    with pytest.raises(AuthorizationRequired):
        await OAuthTokenAuth.create(store, oauth)


# ---------- tests: refresh flow with valid refresh ----------

@pytest.mark.asyncio
async def test_access_missing_but_refresh_valid_triggers_refresh_and_saves(oauth):
    now = int(time.time())
    # access отсутствует; refresh валиден
    tokens = TokenPair(
        access_token=None,
        refresh_token="REFRESH",
        refresh_expires_at_ts=now + 3600,
    )
    store = InMemoryTokenStore(tokens)
    fake_client = FakeHTTPClient([
        FakeResponse(
            status_code=200,
            json_data={"access_token": "NEW_ACCESS", "token_type": "Bearer", "expires_in": 3600},
        )
    ])
    auth = await OAuthTokenAuth.create(store, oauth, http_client=fake_client)

    assert auth.tokens.access_token == "NEW_ACCESS"
    # store.set_tokens должен был обновиться
    assert store._tokens.access_token == "NEW_ACCESS"
    assert store._tokens.token_type == "Bearer"
    assert store._tokens.access_expires_at_ts is not None
    # был 1 вызов на token endpoint
    assert len(fake_client.calls) == 1
    assert fake_client.calls[0]["data"]["grant_type"] == "refresh_token"
    assert fake_client.calls[0]["data"]["refresh_token"] == "REFRESH"
    # client_id попадает в тело запроса (без client_secret используем body-auth)
    assert fake_client.calls[0]["data"]["client_id"] == oauth.client_id

@pytest.mark.asyncio
async def test_access_expired_refresh_valid_triggers_refresh_and_updates_refresh_if_returned(oauth):
    httpx = pytest.importorskip("httpx")  # для raise_for_status совместимых ошибок, если вдруг пригодится
    now = int(time.time())
    tokens = TokenPair(
        access_token="OLD_ACCESS",
        access_expires_at_ts=now - 10,    # просрочен
        refresh_token="OLD_REFRESH",
        refresh_expires_at_ts=now + 3600, # валиден
    )
    store = InMemoryTokenStore(tokens)
    # Эндпойнт вернёт и новый refresh_token
    fake_client = FakeHTTPClient([
        FakeResponse(
            status_code=200,
            json_data={
                "access_token": "NEW_ACCESS",
                "refresh_token": "NEW_REFRESH",
                "token_type": "Bearer",
                "expires_in": 7200
            },
        )
    ])
    auth = await OAuthTokenAuth.create(store, oauth, http_client=fake_client)

    assert auth.tokens.access_token == "NEW_ACCESS"
    assert auth.tokens.refresh_token == "NEW_REFRESH"
    assert store._tokens.refresh_token == "NEW_REFRESH"
    # Проверим, что срок действия пересчитан
    assert auth.tokens.access_expires_at_ts and auth.tokens.access_expires_at_ts > now

@pytest.mark.asyncio
async def test_access_will_expire_within_skew_is_treated_as_expired_and_refreshed(oauth):
    now = int(time.time())
    # access истечёт через 10 сек, skew=30 -> считаем истёкшим
    tokens = TokenPair(
        access_token="SOON_EXPIRES",
        access_expires_at_ts=now + 10,
        refresh_token="REFRESH",
        refresh_expires_at_ts=now + 3600,
    )
    store = InMemoryTokenStore(tokens)
    fake_client = FakeHTTPClient([
        FakeResponse(status_code=200, json_data={"access_token": "NEW", "expires_in": 3600})
    ])
    auth = await OAuthTokenAuth.create(store, oauth, http_client=fake_client)
    assert auth.tokens.access_token == "NEW"
    assert len(fake_client.calls) == 1


# ---------- tests: token endpoint error handling ----------

@pytest.mark.asyncio
async def test_token_endpoint_400_maps_to_authorization_required(oauth):
    # Валидный refresh, но сервер говорит 400 (invalid_grant)
    now = int(time.time())
    store = InMemoryTokenStore(TokenPair(
        refresh_token="R",
        refresh_expires_at_ts=now + 3600,
        access_token=None,
    ))
    fake_client = FakeHTTPClient([FakeResponse(status_code=400, json_data={"error": "invalid_grant"})])
    with pytest.raises(AuthorizationRequired):
        await OAuthTokenAuth.create(store, oauth, http_client=fake_client)

@pytest.mark.asyncio
async def test_token_endpoint_401_or_403_maps_to_authorization_required(oauth):
    # Эти кейсы завязаны на httpx.HTTPStatusError, поэтому потребуем httpx
    httpx = pytest.importorskip("httpx")
    now = int(time.time())
    store = InMemoryTokenStore(TokenPair(
        refresh_token="R",
        refresh_expires_at_ts=now + 3600,
        access_token=None,
    ))
    # 401
    fake_client_401 = FakeHTTPClient([FakeResponse(status_code=401, json_data={"error": "unauthorized"})])
    with pytest.raises(AuthorizationRequired):
        await OAuthTokenAuth.create(store, oauth, http_client=fake_client_401)

    # 403
    store2 = InMemoryTokenStore(TokenPair(
        refresh_token="R",
        refresh_expires_at_ts=now + 3600,
        access_token=None,
    ))
    fake_client_403 = FakeHTTPClient([FakeResponse(status_code=403, json_data={"error": "forbidden"})])
    with pytest.raises(AuthorizationRequired):
        await OAuthTokenAuth.create(store2, oauth, http_client=fake_client_403)

@pytest.mark.asyncio
async def test_token_endpoint_500_maps_to_auth_refresh_error(oauth):
    now = int(time.time())
    store = InMemoryTokenStore(TokenPair(
        refresh_token="R",
        refresh_expires_at_ts=now + 3600,
        access_token=None,
    ))
    fake_client = FakeHTTPClient([FakeResponse(status_code=500, json_data={"error": "server"})])
    with pytest.raises(AuthRefreshError):
        await OAuthTokenAuth.create(store, oauth, http_client=fake_client)


# ---------- tests: no refresh needed (access valid) ----------

@pytest.mark.asyncio
async def test_access_valid_no_refresh_call(oauth):
    now = int(time.time())
    store = InMemoryTokenStore(TokenPair(
        access_token="VALID",
        access_expires_at_ts=now + 3600,
        refresh_token="R",
        refresh_expires_at_ts=now + 7200,
    ))
    fake_client = FakeHTTPClient([])  # не должно быть вызовов
    auth = await OAuthTokenAuth.create(store, oauth, http_client=fake_client)
    assert auth.tokens.access_token == "VALID"
    assert len(fake_client.calls) == 0


# ---------- tests: JSONFileTokenStore persistence on refresh ----------

@pytest.mark.asyncio
async def test_json_file_store_persists_tokens_on_refresh(tmp_path, oauth):
    now = int(time.time())
    path = tmp_path / "tokens.json"
    store = JSONFileTokenStore(path)

    # предварительно положим в файл refresh-токен (в реале это делает set_tokens ранее)
    data = {
        "refresh_token": "R",
        "refresh_expires_at_ts": now + 3600,
    }
    path.write_text(json.dumps(data), encoding="utf-8")

    fake_client = FakeHTTPClient([
        FakeResponse(status_code=200, json_data={"access_token": "NEW", "expires_in": 111})
    ])
    auth = await OAuthTokenAuth.create(store, oauth, http_client=fake_client)

    # файл должен обновиться set_tokens-ом
    saved = json.loads(path.read_text(encoding="utf-8"))
    assert saved["access_token"] == "NEW"
    assert saved["access_expires_at_ts"] >= now


# ---------- tests: CallableTokenStore getter/setter ----------

@pytest.mark.asyncio
async def test_callable_store_get_set(oauth):
    now = int(time.time())
    storage = {"tokens": TokenPair(
        access_token=None,
        refresh_token="R",
        refresh_expires_at_ts=now + 3600,
    )}

    async def getter():
        return storage["tokens"]

    set_called = {"flag": False}
    async def setter(t: TokenPair):
        set_called["flag"] = True
        storage["tokens"] = t

    store = CallableTokenStore(getter=getter, setter=setter)
    fake_client = FakeHTTPClient([
        FakeResponse(status_code=200, json_data={"access_token": "NEW", "expires_in": 42})
    ])
    auth = await OAuthTokenAuth.create(store, oauth, http_client=fake_client)
    assert set_called["flag"] is True
    assert storage["tokens"].access_token == "NEW"
