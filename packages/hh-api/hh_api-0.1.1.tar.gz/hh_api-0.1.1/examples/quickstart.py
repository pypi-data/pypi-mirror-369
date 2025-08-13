# quickstart.py
import asyncio

import httpx


async def get_access_token(client_id, client_secret):
    DEFAULT_TOKEN_URL = "https://api.hh.ru/token"

    data = {
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret,
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(DEFAULT_TOKEN_URL, data=data)
        response.raise_for_status()
        access_token = response.json()["access_token"]
        print(access_token)
        return access_token


async def search_similar_vacancies(access_token: str, text: str, resume_id: str, per_page: int = 10):
    url = f"https://api.hh.ru/resumes/{resume_id}/similar_vacancies"

    params = {
        "text": text,
        "search_field": "name",
        "schedule": "remote",
        "per_page": per_page,
        "page": 0,
        "order_by": "relevance"
    }

    headers = {
        "Authorization": f"Bearer {access_token}",
        "User-Agent": "HH-Assistant-bot"
    }
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params, headers=headers)
            response.raise_for_status()
            data = response.json()
            return data.get("items", [])
    except httpx.HTTPStatusError as e:
        print(f"Ошибка HTTP: {e.response.status_code} - {e.response.text}")
        return []
    except Exception as e:
        print(f"Ошибка при выполнении запроса: {e}")
        return []


async def search_vacancies(access_token, text):
    url = "https://api.hh.ru/vacancies"
    params = {
        "text": text,
        "search_field": "name",
        "schedule": "remote",
        "per_page": 10,
        "page": 0,
        "order_by": "relevance"
    }
    headers = {
        "Authorization": f"Bearer {access_token}",
        "User-Agent": "HH-Assistant-bot"
    }
    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params, headers=headers)
        response.raise_for_status()
        data = response.json()
        return data


def apply_to_vacancy(access_token, resume_id: str, vacancy_id: str, message: str) -> bool:
    """
    Откликается на вакансию от имени активного резюме.

    Args:
        resume_id (str): ID резюме
        vacancy_id (str): ID вакансии, на которую подаётся отклик.
        message (str): Сопроводительное письмо для отклика.

    Returns:
        bool: True, если отклик успешен, False в случае ошибки.

    Note:
        Требуется действующий OAuth2-токен для авторизации.
        Функция предполагает наличие функции get_active_resume_id(), возвращающей ID активного резюме.
    """

    url = "https://api.hh.ru/negotiations"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "User-Agent": "HH-Assistant-bot"
    }
    data = {
        "vacancy_id": vacancy_id,
        "resume_id": resume_id,
        "message": message
    }

    try:
        with httpx.Client() as client:
            response = client.post(url, headers=headers, data=data)
            response.raise_for_status()
            print("Отклик на вакансию успешно отправлен")
            return True
    except httpx.HTTPStatusError as e:
        print(f"Ошибка HTTP: {e.response.status_code} - {e.response.text}")
        return False
    except httpx.RequestError as e:
        print(f"Ошибка запроса: {e}")
        return False


if __name__ == "__main__":

    # token = asyncio.run(get_access_token(client_id, client_secret))
    token = "USERLT95AQ8M4L6KV07GTKGHKR38C80S5K5HH4G8U1JFK8QSUA1T22L930O6DKTL"
    # token = "APPLLD20LAHRH3TGNE3EO2B7KQ111SDMBAAJPDBRKA00GUS5MB0V40RS1554IPS4"

    resume_id = "40e3574aff0eae014a0039ed1f516453674645"
    text = "php"

    # similar_vacancies = asyncio.run(search_similar_vacancies(access_token, text, resume_id))
    # print(similar_vacancies)

    # vacancies = asyncio.run(search_vacancies(token, text))
    # print(vacancies)

    message = ''' Добрый день!

'''

    apply_to_vacancy(token, resume_id, "117459005", message)

    # asyncio.run(main())
