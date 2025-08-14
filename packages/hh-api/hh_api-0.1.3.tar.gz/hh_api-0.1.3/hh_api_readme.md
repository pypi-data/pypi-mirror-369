## 📦 деплой библиотеки

```bash
hatch version patch
Remove-Item -Recurse -Force dist, build, *.egg-info -ErrorAction SilentlyContinue
python -m build
$env:TWINE_USERNAME = "__token__"
$env:TWINE_PASSWORD = "pypi-AgEIcHlwaS5vcmcCJDhlMzY0MTQwLWQzMzktNDc1MC1iN2Y1LTAyNWZlMTU1NDA4NQACDlsxLFsiaGgtYXBpIl1dAAIsWzIsWyJmMWJhOTc4Yy0xNzhkLTRmODctYmY0Yi1hYTA3OTRjYzY4YWEiXV0AAAYgvloK9DQT2Q3vg1qIHU1aJ_TPOM_iT6hDHTF_cEnPjBY"
twine upload dist/*
```
