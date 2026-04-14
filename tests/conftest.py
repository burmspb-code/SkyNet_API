"""Модуль конфигурации для pytest"""

from unittest.mock import patch

import pytest

from src.base import SkyMapCoordinator
from src.utils.api_adapter import OpenApiIntegrator
from src.utils.token_open_sky import TokenManager


@pytest.fixture
def integrator():
    return OpenApiIntegrator()


@pytest.fixture
def mock_token_headers(mocker):
    # Мокаем TokenManager, чтобы не зависеть от его логики
    return mocker.patch(
        "src.utils.token_open_sky.TokenManager.headers",
        return_value={"Authorization": "Bearer test"},
    )


@pytest.fixture
def manager():
    return TokenManager()


@pytest.fixture
def mock_coordinator():
    """Фикстура для подмены логики OpenSky"""
    with patch("src.aircraft_collector.SkyMapCoordinator") as mock:
        instance = mock.return_value
        # Эмулируем базу стран
        instance.extraction_countries.return_value = {
            "австрия": [46, 49, 9, 17],
            "austria": [46, 49, 9, 17],
        }
        # Эмулируем ответ API (один самолет)
        instance.extraction_aircraft_info.return_value = {
            "states": [
                [
                    "icao123",
                    "CALLSIGN",
                    "Austria",
                    1705000000,
                    1705000000,
                    10.0,
                    47.0,
                    5000.0,
                    False,
                    250.0,
                    180.0,
                    0.0,
                    None,
                    5000.0,
                    "1234",
                    False,
                    0,
                ]
            ]
        }
        yield instance


@pytest.fixture
def mock_storage():
    """Подменяем класс JsonAircraftStorage там, где он используется"""
    with patch("src.aircraft_collector.JsonAircraftStorage") as mock_class:
        # Возвращаем объект, который "создастся" внутри функции
        yield mock_class.return_value


@pytest.fixture
def coordinator():
    # Мокаем родительские методы, чтобы не было реальных сетевых запросов
    with (
        patch("src.base.OpenApiIntegrator.get_countries_checklist"),
        patch("src.base.OpenApiIntegrator.get_border_country"),
        patch("src.base.OpenApiIntegrator.get_os_info"),
    ):
        yield SkyMapCoordinator()
