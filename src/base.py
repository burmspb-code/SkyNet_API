"""Описние базовых классов проекта"""

from abc import ABC, abstractmethod
from typing import Any

from src.utils.API_adapter import OpenApiIntegrator
from src.utils.token_OpenSky import TokenManager


class BaseSkyMapCoordinator(ABC):
    """Абстрактный базовый класс для работы с OpenStreetMap и OpenSky"""

    @abstractmethod
    def extraction_border_country(self, country_name: str) -> Any:
        """Метод получения координат страны"""
        pass

    @abstractmethod
    def extraction_countries_list(self) -> list:
        """Метод получения списка стран"""
        pass

    @abstractmethod
    def extraction_aircraft_info(self, border_country: str) -> Any:
        """Метод получения информации о самолетах"""
        pass


class SkyMapCoordinator(BaseSkyMapCoordinator, OpenApiIntegrator):
    """Получение и обработка данных с OpenSreetMap и OpenSky"""

    def __init__(self) -> None:
        # Используем быстрое зеркало

        super().__init__()

    @property
    def extraction_countries_list(self) -> list:
        """Получения списка стран"""

        # Передаем запрос  через POST
        data = self.get_countries_checklist

        countries = {}
        for element in data.get('elements', []):
            tags = element.get('tags', {})
            iso_code = tags.get('ISO3166-1:alpha2') or tags.get('ISO3166-1')
            name = tags.get('name:ru') or tags.get('name')

            if name and iso_code:
                countries[name] = iso_code

        # Сортируем по названию для удобства
        return dict(sorted(countries.items(), key=lambda item: item[1]))

    def extraction_border_country(self, country_name: str) -> Any:
        """Метод получения коордиант - кортедж (широта, долгота) по коду страны"""

        data = self.get_border_country(country_name)

        # Проверяем, что пришел не пустой список
        if isinstance(data, list) and len(data) > 0:
            first_result = data[0]
            bbox = first_result.get('boundingbox', [])

            if len(bbox) == 4:
                # Nominatim отдает: [southLat, northLat, westLon, eastLon]
                # Превращаем в числа
                lat_min, lat_max, lon_min, lon_max = [float(x) for x in bbox]

                # Возвращаем словарь, который удобно распаковать в параметры запроса
                return {
                    "lamin": lat_min,
                    "lamax": lat_max,
                    "lomin": lon_min,
                    "lomax": lon_max
                }

        return {}  # Или выкинуть исключение, если данные не найдены

    def extraction_aircraft_info(self, border) -> Any:
        """Метод получения данных о самолетах над определенной рамкой"""

        data = self.get_os_info(border)
        return data
