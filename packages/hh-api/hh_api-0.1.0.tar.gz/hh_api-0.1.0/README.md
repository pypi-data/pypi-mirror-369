# hhru-async

Async Python client for the HeadHunter (hh.ru) API.
Built on `httpx`, includes token auto-refresh (OAuth2 refresh token flow), retries, and helpers.

See `pyproject.toml` for metadata.

## Quickstart

```bash
pip install hh-api
```

```python
import asyncio
from hh_api import HHClient, StaticTokenAuth

async def main():
    auth = StaticTokenAuth("YOUR_ACCESS_TOKEN")
    client = HHClient(auth)
    vac = await client.get_vacancy("123456")
    print(vac["name"])
    await client.aclose()

asyncio.run(main())
```

## Development

Build:
```bash
pipx install hatch
hatch build
```

Publish:
```bash
python -m pip install --upgrade twine
twine upload dist/*
```
