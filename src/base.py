from abc import ABC, abstractmethod

from src.utils.mixins import HttpClientMixin


class BaseCountryLocator(ABC):
    """Абстрактный базовый класс для получения координат страны"""

    @abstractmethod
    def get_coordinates(self, country_code: str) -> tuple[float, float]:
        """Метод получения коордиант - кортедж (широта, долгота) по названию страны"""
        pass

class BaseCountryListOpenStreetMap(ABC):
    """Абстрактный базовый класс для получения списка стран сервиса OpenStreetMap"""

    @property
    @abstractmethod
    def get_country(self) -> list:
        """Метод получения списка стран"""
        pass

class CountryList(BaseCountryListOpenStreetMap, HttpClientMixin):
    """Отправляет запрос к Overpass API и выводит названия стран и их коды ISO"""
    def __init__(self) -> None:
        # Используем более быстрое зеркало
        self.url = "https://overpass.openstreetmap.fr/api/interpreter"
        self.overpass_query = '[out:json][timeout:25];relation["admin_level"="2"]["ISO3166-1"];out tags;'
        super().__init__()

    @property
    def get_country(self) -> list:
        """Получения списка стран"""
        # Передаем запрос в параметре 'data' через POST
        payload = {'data': self.overpass_query}
        data = self._post(self.url, data=payload)

        countries = {}
        for element in data.get('elements', []):
            tags = element.get('tags', {})
            name = tags.get('name:ru') or tags.get('name')  # Пытаемся взять русское название
            iso_code = tags.get('ISO3166-1')

            if name and iso_code:
                countries[iso_code] = name

        # Сортируем по названию для удобства
        return dict(sorted(countries.items(), key=lambda item: item[1]))
