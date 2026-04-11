"""Модуль для взаимодействия с API-сервисами OpenStreetMap и OpenSky"""

import requests
from requests.exceptions import RequestException, JSONDecodeError
from abc import ABC, abstractmethod

class BaseOpenApiIntegrator(ABC):
    """Абстрактный класс для взаимодествия по API"""

    @abstractmethod
    def get_countries_checklist(self) -> Any:
        """Получение перечня стран"""
        pass

    @abstractmethod
    def get_border_country(self, country_name: str) -> Any:
        """Получение границы страны"""

    @abstractmethod
    def get_os_info(self) -> Any:
        """Получение информации о самолетах OS"""
        pass


class OpenApiIntegrator(BaseOpenApiIntegrator):
    """Класс для выполнения http запросов"""
    __overpass_query = '[out:json][timeout:25];relation["admin_level"="2"]["ISO3166-1"];out tags;'
    __url_overpass = "https://overpass.openstreetmap.fr/api/interpreter"
    __url_nominatim = 'https://nominatim.openstreetmap.org/search'

    def __init__(self):
        self.country_name = None
        self.payload = {'data': self.__overpass_query}

        print("Подключение к сервисам OpenStreetMap и OpenSky")

    def __post_osm(self) -> Any:
        """Отправка POST-запроса на overpass для получения списка стран с кодами"""
        headers = {
            'User-Agent': 'SkyNet_API/1.0',
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        # Инициализируем переменную заранее
        response = None

        print(f"Отправка POST запроса на {self.__url_overpass}")

        try:
            response = requests.post(self.__url_overpass, data=self.payload, headers=headers, timeout=60)
            print(f"Статус ответа: {response.status_code}")
            response.raise_for_status()
            return response.json()

        except JSONDecodeError:
            print(f"Ошибка парсинга JSON. Получен HTML/текст: {response.text[:200]}...")
            return {}

        except RequestException as e:
            # Логируем сетевые ошибки (504, 404, Connection Error и т.д.)
            print(f"Сетевая ошибка при запросе к {self.__overpass_query}: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Тело ошибки: {e.response.text}")
            return {}
        except Exception as e:
            print(f"Непредвиденная ошибка: {e}")
            return {}

    def __get_osm(self, country_name: str) -> Any:
        """Отправка GET-запроса для получения границы (рамки) объекта"""
        # Headers с user-agent - обязательный параметр при запросе к nominatim.openstreetmap.
        headers = {'User-Agent': 'SkyNet_API/1.0'}
        params = {'country': country_name, 'format': 'json', 'limit': 1}

        # Инициализируем переменную заранее
        response = None

        print(f"Отправка GET запроса на {self.__url_nominatim}")

        try:
            response = requests.get(self.__url_nominatim, params=params, headers=headers, timeout=20)
            print(f"Статус ответа: {response.status_code}")
            response.raise_for_status()
            return response.json()

        except JSONDecodeError:
            print(f"Ошибка парсинга JSON. Получен HTML/текст: {response.text[:200]}...")
            return {}

        except RequestException as e:
            # Логируем сетевые ошибки (504, 404, Connection Error и т.д.)
            print(f"Сетевая ошибка при запросе к {self.__url_nominatim}: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Тело ошибки: {e.response.text}")
            return {}
        except Exception as e:
            print(f"Непредвиденная ошибка: {e}")
            return {}

    def get_os_info(self) -> Any:
        """Получение информации о самолетах"""
        pass

    @property
    def get_countries_checklist(self) -> Any:
        """Получение перечня стран с ресурса OpenStreetMap"""
        return self.__post_osm()

    def get_border_country(self, country_name: str) -> Any:
        """Получение границы страны"""
        return self.__get_osm(country_name)
