"""Модуль для взаимодействия с API-сервисами OpenStreetMap и OpenSky"""

from abc import ABC, abstractmethod
from typing import Any, Dict

import requests
from requests.exceptions import JSONDecodeError, RequestException

from src.utils.logging_config import setup_logger
from src.utils.token_open_sky import TokenManager

logger = setup_logger("api_adapter")


class BaseOpenApiIntegrator(ABC):
    """Абстрактный класс для взаимодествия по API"""

    @abstractmethod
    def get_countries_checklist(self) -> Any:
        """Получение перечня стран от OSM"""
        pass

    @abstractmethod
    def get_border_country(self, country_name: str) -> Any:
        """Получение границы страны от OSM"""

    @abstractmethod
    def get_os_info(self, border_country: Dict[str, float]) -> Any:
        """Получение информации о самолетах от OS"""
        pass


class OpenApiIntegrator(BaseOpenApiIntegrator):
    """Класс для выполнения http запросов"""

    def __init__(self):
        self.__overpass_query = (
            '[out:json][timeout:25];relation["admin_level"="2"]["ISO3166-1"];out tags;'
        )
        self.__url_overpass = "https://overpass.openstreetmap.fr/api/interpreter"
        self.__url_nominatim = "https://nominatim.openstreetmap.org/search"
        self.__token_manager = TokenManager()
        self.__url_base_os = "https://opensky-network.org/api"
        self.country_name = None

    @staticmethod
    def _safe_request(method: str, url: str, **kwargs) -> Any:
        """Метод защищенного подключения через request"""

        # Инициализируем переменную заранее
        response = None
        try:
            # Используем универсальный requests.request
            response = requests.request(method, url, timeout=60, **kwargs)
            logger.info(
                f"Отправка запроса на {url}; Статус ответа: {response.status_code}"
            )
            response.raise_for_status()
            return response.json()
        except JSONDecodeError:
            content = (
                response.text[:200] if response is not None else "Нет ответа response"
            )
            logger.error(f"Ошибка парсинга JSON. Получен HTML/текст: {content}...")
            return {}
        except RequestException as e:
            # Логируем сетевые ошибки (504, 404, Connection Error и т.д.)
            logger.error(f"Сетевая ошибка при запросе {url}: {e}")
            if hasattr(e, "response") and e.response is not None:
                logger.error(f"Тело ошибки: {e.response.text}")
            return {}
        except Exception as e:
            logger.error(f"Непредвиденная ошибка: {e}")
            return {}

    def __post_osm(self) -> Any:
        """Отправка POST-запроса на overpass для получения списка стран с кодами"""
        headers = {
            "User-Agent": "SkyNet_API/1.0",
            "Content-Type": "application/x-www-form-urlencoded",
        }
        payload = {"data": self.__overpass_query}
        return self._safe_request(
            "POST", self.__url_overpass, headers=headers, data=payload
        )

    def __get_osm(self, country_name: str) -> Any:
        """Отправка GET-запроса для получения границы (рамки) объекта"""
        # Headers с user-agent - обязательный параметр при запросе к nominatim.openstreetmap.
        headers = {"User-Agent": "SkyNet_API/1.0"}
        params = {"country": country_name, "format": "json", "limit": 1}
        return self._safe_request(
            "GET", self.__url_nominatim, headers=headers, params=params
        )

    def __get_os(self, border_country: Dict[str, float]) -> Any:
        """Получение информации о самолетах"""

        query_params = {
            "lamin": border_country["lamin"],
            "lomin": border_country["lomin"],
            "lamax": border_country["lamax"],
            "lomax": border_country["lomax"],
        }

        url = f"{self.__url_base_os}/states/all"

        return self._safe_request(
            "GET", url, headers=self.__token_manager.headers(), params=query_params
        )

    def get_countries_checklist(self) -> Any:
        """Получение перечня стран с ресурса OpenStreetMap"""
        return self.__post_osm()

    def get_border_country(self, country_name: str) -> Any:
        """Получение границы страны с ресурса OpenStreetMap"""
        return self.__get_osm(country_name)

    def get_os_info(self, border_country: Dict[str, float]) -> Any:
        """Получение информации о самолетах с ресурса OpenSky"""
        return self.__get_os(border_country)
