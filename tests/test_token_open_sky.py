"""Тестирование модуля для получения/оновления токена длял OpenSky"""

import pytest
import requests
from datetime import datetime, timedelta
from unittest.mock import patch
from src.utils.token_open_sky import TokenManager, TOKEN_URL  # замените your_module_name на имя вашего файла


def test_refresh_sets_token_and_expiry(manager, requests_mock):
    """Проверка, что _refresh корректно сохраняет токен и время истечения."""
    mock_response = {
        "access_token": "fake_token_123",
        "expires_in": 3600
    }
    requests_mock.post(TOKEN_URL, json=mock_response)

    token = manager._refresh()

    assert token == "fake_token_123"
    assert manager.token == "fake_token_123"
    assert manager.expires_at > datetime.now()


def test_get_token_returns_existing_valid_token(manager):
    """Проверка, что валидный токен не обновляется повторно."""
    manager.token = "valid_token"
    # Ставим срок истечения в будущем (через 10 минут)
    manager.expires_at = datetime.now() + timedelta(minutes=10)

    with patch.object(TokenManager, '_refresh') as mock_refresh:
        token = manager.get_token()
        assert token == "valid_token"
        mock_refresh.assert_not_called()


def test_get_token_refreshes_if_expired(manager, requests_mock):
    """Проверка автоматического обновления, если токен просрочен."""
    manager.token = "expired_token"
    # Ставим срок истечения в прошлом
    manager.expires_at = datetime.now() - timedelta(seconds=10)

    requests_mock.post(TOKEN_URL, json={"access_token": "new_token", "expires_in": 60})

    token = manager.get_token()
    assert token == "new_token"
    assert requests_mock.called


def test_headers_format(manager, requests_mock):
    """Проверка формирования заголовка Authorization."""
    requests_mock.post(TOKEN_URL, json={"access_token": "abc", "expires_in": 60})

    expected_headers = {"Authorization": "Bearer abc"}
    assert manager.headers() == expected_headers


def test_refresh_error_raises_exception(manager, requests_mock):
    """Проверка обработки ошибки сервера (401, 500 и т.д.)."""
    requests_mock.post(TOKEN_URL, status_code=401)

    with pytest.raises(requests.exceptions.HTTPError):
        manager._refresh()