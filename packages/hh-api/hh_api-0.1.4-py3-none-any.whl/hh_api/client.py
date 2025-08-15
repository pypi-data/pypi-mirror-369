from __future__ import annotations

import asyncio
from typing import Any, Dict, Optional, List, Union
import httpx

from .auth import TokenManager
from .exceptions import HHAPIError, HHAuthError, HHNetworkError

DEFAULT_BASE_URL = "https://api.hh.ru"
DEFAULT_USER_AGENT = "hh-api (+https://github.com/inetsmol/hh-api)"

Subject = Union[int, str]


class HHClient:
    """
    Простой HTTP-клиент к HH API поверх TokenManager (multi-tenant).
    subject — это идентификатор пользователя (tg_id, user_id и т.п.), чьи токены будем использовать.
    """

    def __init__(
        self,
        tm: TokenManager[Subject],
        *,
        subject: Optional[Subject] = None,
        base_url: str = DEFAULT_BASE_URL,
        user_agent: str = DEFAULT_USER_AGENT,
        timeout: float = 20.0,
        retries: int = 3,
        backoff_base: float = 0.5,
        transport: Optional[httpx.AsyncBaseTransport] = None,
    ) -> None:
        self.tm = tm
        self.subject = subject
        self.base_url = base_url.rstrip("/")
        self.user_agent = user_agent
        self.retries = retries
        self.backoff_base = backoff_base
        self._client = httpx.AsyncClient(transport=transport, timeout=timeout)

    async def aclose(self) -> None:
        await self._client.aclose()

    async def _auth_headers(self, *, subject: Optional[Subject]) -> Dict[str, str]:
        """Получить заголовки авторизации для конкретного subject."""
        # определяем, для кого берём токен
        s = subject if subject is not None else self.subject
        if s is None:
            raise ValueError("subject (user_id) не задан: укажите в конструкторе или при вызове метода.")

        # получаем валидный access_token и собираем заголовки
        access = await self.tm.ensure_access(s)  # <- важно: ensure_access(subject) (multi-tenant)
        headers = self.tm.get_auth_header(access)
        headers.setdefault("Accept", "application/json")
        headers.setdefault("User-Agent", self.user_agent)
        return headers

    async def _request(
        self,
        method: str,
        path: str,
        *,
        subject: Optional[Subject] = None,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> httpx.Response:
        url = f"{self.base_url}{path}"
        last_exc: Optional[Exception] = None

        for attempt in range(1, self.retries + 1):
            try:
                req_headers = await self._auth_headers(subject=subject)
                if headers:
                    req_headers.update(headers)

                resp = await self._client.request(
                    method, url, params=params, data=data, json=json, headers=req_headers
                )

                # авторизационные ошибки пробрасываем как HHAuthError
                if resp.status_code in (401, 403):
                    # У многих интеграций это значит «нужно переавторизовать пользователя».
                    raise HHAuthError(resp.status_code, resp.text)

                if resp.status_code >= 400:
                    raise HHAPIError(resp.status_code, resp.text)

                return resp

            except httpx.RequestError as e:
                last_exc = e
                if attempt < self.retries:
                    await asyncio.sleep(self.backoff_base * (2 ** (attempt - 1)))
                    continue
                raise HHNetworkError(str(e)) from e

            except HHAPIError as e:
                last_exc = e
                # 5xx — можно попробовать повторить
                if 500 <= getattr(e, "status_code", 0) < 600 and attempt < self.retries:
                    await asyncio.sleep(self.backoff_base * (2 ** (attempt - 1)))
                    continue
                raise

        assert last_exc is not None
        raise last_exc

    # ---------------------------
    # Публичные методы API
    # ---------------------------

    async def get_resume(self, resume_id: str, *, subject: Optional[Subject] = None) -> Dict[str, Any]:
        return (await self._request("GET", f"/resumes/{resume_id}", subject=subject)).json()

    async def get_vacancy(self, vacancy_id: str, *, subject: Optional[Subject] = None) -> Dict[str, Any]:
        return (await self._request("GET", f"/vacancies/{vacancy_id}", subject=subject)).json()

    async def get_dictionaries(self, *, subject: Optional[Subject] = None) -> Dict[str, Any]:
        return (await self._request("GET", "/dictionaries", subject=subject)).json()

    async def search_similar_vacancies(
        self,
        *,
        resume_id: str,
        subject: Optional[Subject] = None,
        text: Optional[str] = None,
        search_field: str = "name",
        salary: Optional[int] = None,
        currency: Optional[str] = None,
        schedule: Optional[str] = None,
        per_page: int = 25,
        page: int = 0,
        order_by: str = "relevance",
        extra_params: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        params: Dict[str, Any] = {"per_page": per_page, "page": page, "order_by": order_by}
        if text:
            params["text"] = text
        if search_field:
            params["search_field"] = search_field
        if salary is not None:
            params["salary"] = salary
        if currency:
            params["currency"] = currency
        if schedule:
            params["schedule"] = schedule
        if extra_params:
            params.update(extra_params)

        data = (
            await self._request("GET", f"/resumes/{resume_id}/similar_vacancies", subject=subject, params=params)
        ).json()
        return data.get("items", [])

    async def apply_to_vacancy(
        self, *, resume_id: str, vacancy_id: str, message: str, subject: Optional[Subject] = None
    ) -> bool:
        resp = await self._request(
            "POST",
            "/negotiations",
            subject=subject,
            data={"vacancy_id": vacancy_id, "resume_id": resume_id, "message": message},
        )
        return resp.status_code in (200, 201, 202, 204)
