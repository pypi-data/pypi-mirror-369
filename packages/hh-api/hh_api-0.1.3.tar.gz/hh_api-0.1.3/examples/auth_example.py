import asyncio
import os
from pathlib import Path

from dotenv import load_dotenv

from hh_api.auth import JSONDirTokenStore, TokenManager, OAuthConfig

load_dotenv()

# Каталог для хранения токенов (кроссплатформенно, в домашней папке пользователя)
TOKENS_DIR = Path.home() / ".hh_tokens"   # например: /home/user/.hh_tokens / C:\Users\...\ .hh_tokens
print(TOKENS_DIR)
TOKENS_DIR.mkdir(parents=True, exist_ok=True)

# Ваш User-Agent обязателен для всех запросов к hh API
USER_AGENT = "auto-cover-letter-bot/1.0"


# Рекомендуется хранить секреты в окружении (или pydantic-settings)
CLIENT_ID = os.getenv("HH_CLIENT_ID")
CLIENT_SECRET = os.getenv("HH_CLIENT_SECRET")
REDIRECT_URI = os.getenv("HH_REDIRECT_URI")


# Конфиг OAuth (правильный token_url уже внутри класса из примера)
oauth_cfg = OAuthConfig(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    redirect_uri=REDIRECT_URI,
)

# JSON сторадж: на каждого пользователя — отдельный файл <subject>.json
store = JSONDirTokenStore(TOKENS_DIR)

# Менеджер токенов (универсальный — работает с любым KeyedTokenStore)
tm = TokenManager(oauth_cfg, store, user_agent=USER_AGENT)


async def hh_link(uid: int):
    """
    1) Генерируем ссылку авторизации для пользователя.
       В параметр state можно передать uid (или подписанный токен), чтобы связать колбэк с пользователем.
    """
    # state лучше подписывать/хешировать, но для примера используем uid в явном виде
    url = tm.authorization_url(subject=uid, state=str(uid))
    # В реальном приложении — сделайте редирект на эту ссылку; здесь вернём как текст.
    return url

async def hh_callback(subject: int, code: str):
    """
    2) Колбэк, на который HH сделает редирект с параметрами ?code=...&state=...
       Здесь обмениваем code на токены и сохраняем в JSON файле subject-а.
    """
    # Обменять code на токены и сохранить в JSON
    try:
        tokens = await tm.exchange_code(subject, code)
        return tokens
    except Exception as e:
        print(e)


async def main():
    user_tg_id = 12345678
    # # Генерируем ссылку
    # link = await hh_link(uid=user_tg_id)
    # print(link)
    # # Колбэк
    # code = input("Enter code: ")
    # tokens = await hh_callback(subject=user_tg_id, code=code)
    # print(tokens)

    token = await tm.ensure_access(subject=user_tg_id)
    print(token)


if __name__ == "__main__":
    asyncio.run(main())