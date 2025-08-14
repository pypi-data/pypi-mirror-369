import asyncio
from typing import Any, Dict, Optional, List
import httpx

from . import OAuthTokenAuth
from .exceptions import HHAPIError, HHAuthError, HHNetworkError
from .utils import extract_job_description_from_vacancy

DEFAULT_BASE_URL = "https://api.hh.ru"
DEFAULT_USER_AGENT = "hh-api/0.1.0 (+https://github.com/yourname/hh-api)"

class HHClient:
    def __init__(self, auth: OAuthTokenAuth, *, base_url: str = DEFAULT_BASE_URL,
                 user_agent: str = DEFAULT_USER_AGENT, timeout: float = 20.0,
                 retries: int = 3, backoff_base: float = 0.5,
                 transport: Optional[httpx.AsyncBaseTransport] = None) -> None:
        self.auth = auth
        self.base_url = base_url.rstrip("/")
        self.user_agent = user_agent
        self.timeout = timeout
        self.retries = retries
        self.backoff_base = backoff_base
        self._client = httpx.AsyncClient(transport=transport, timeout=timeout)

    async def aclose(self) -> None:
        await self._client.aclose()

    async def _request(self, method: str, path: str, *, params: Optional[Dict[str, Any]] = None,
                       data: Optional[Dict[str, Any]] = None, json: Optional[Dict[str, Any]] = None,
                       headers: Optional[Dict[str, str]] = None) -> httpx.Response:
        url = f"{self.base_url}{path}"; last_exc: Optional[Exception] = None
        for attempt in range(1, self.retries + 1):
            try:
                token = await self.auth.ensure_fresh_token()
                req_headers = {"Authorization": f"Bearer {token}", "User-Agent": self.user_agent, "Accept": "application/json"}
                if headers: req_headers.update(headers)
                resp = await self._client.request(method, url, params=params, data=data, json=json, headers=req_headers)
                if resp.status_code in (401, 403) and attempt < self.retries:
                    await asyncio.sleep(self.backoff_base * attempt); continue
                if resp.status_code >= 400:
                    if resp.status_code in (401, 403): raise HHAuthError(resp.status_code, resp.text)
                    raise HHAPIError(resp.status_code, resp.text)
                return resp
            except httpx.RequestError as e:
                last_exc = e
                if attempt < self.retries:
                    await asyncio.sleep(self.backoff_base * (2 ** (attempt - 1))); continue
                raise HHNetworkError(str(e)) from e
            except HHAPIError as e:
                last_exc = e
                if 500 <= getattr(e, "status_code", 0) < 600 and attempt < self.retries:
                    await asyncio.sleep(self.backoff_base * (2 ** (attempt - 1))); continue
                raise
        assert last_exc is not None; raise last_exc

    async def get_resume(self, resume_id: str) -> Dict[str, Any]:
        return (await self._request("GET", f"/resumes/{resume_id}")).json()

    async def get_vacancy(self, vacancy_id: str) -> Dict[str, Any]:
        return (await self._request("GET", f"/vacancies/{vacancy_id}")).json()

    async def get_dictionaries(self) -> Dict[str, Any]:
        return (await self._request("GET", "/dictionaries")).json()

    async def search_similar_vacancies(self, *, resume_id: str, text: Optional[str] = None, search_field: str = "name",
                                       salary: Optional[int] = None, currency: Optional[str] = None,
                                       schedule: Optional[str] = None, per_page: int = 25, page: int = 0,
                                       order_by: str = "relevance", extra_params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        params: Dict[str, Any] = {"per_page": per_page, "page": page, "order_by": order_by}
        if text: params["text"] = text
        if search_field: params["search_field"] = search_field
        if salary is not None: params["salary"] = salary
        if currency: params["currency"] = currency
        if schedule: params["schedule"] = schedule
        if extra_params: params.update(extra_params)
        data = (await self._request("GET", f"/resumes/{resume_id}/similar_vacancies", params=params)).json()
        return data.get("items", [])

    async def apply_to_vacancy(self, *, resume_id: str, vacancy_id: str, message: str) -> bool:
        resp = await self._request("POST", "/negotiations", data={"vacancy_id": vacancy_id, "resume_id": resume_id, "message": message})
        return resp.status_code in (200, 201, 202, 204)

    @staticmethod
    def extract_job_description_from_vacancy(vacancy):
        return extract_job_description_from_vacancy(vacancy)
