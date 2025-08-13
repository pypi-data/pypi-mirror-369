def test_import():
    import hh_api
    # пока проверяем наличие публичного API из auth
    assert hasattr(hh_api, "OAuthTokenAuth")
