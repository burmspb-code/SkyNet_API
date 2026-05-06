"""Модуль с описанием базовых классов проекта"""

from abc import ABC, abstractmethod
from typing import Any, Dict

from src.utils.api_adapter import OpenApiIntegrator
from src.utils.logging_config import setup_logger

logger = setup_logger("base")


class BaseSkyMapCoordinator(ABC):
    """Абстрактный базовый класс для работы с OpenStreetMap и OpenSky"""

    @abstractmethod
    def extraction_border_country(self, country_name: str) -> Any:
        """Метод получения координат страны"""
        pass

    @abstractmethod
    def extraction_countries(self) -> list:
        """Метод получения списка стран"""
        pass

    @abstractmethod
    def extraction_aircraft_info(self, border_country: Dict[str, float]) -> Any:
        """Метод получения информации о самолетах"""
        pass


class AircraftStorage(ABC):
    """Абстрактный класс для хранилищ данных о самолетах"""

    @abstractmethod
    def add_aircraft(self, aircraft_data: dict):
        """Добавить информацию о самолете в файл"""
        pass

    @abstractmethod
    def get_aircraft(self, criteria: dict):
        """Получить данные из файла по критериям (например, {'callsign': 'AEE995'})"""
        pass

    @abstractmethod
    def delete_aircraft(self, icao24: str):
        """Удалить информацию о самолете по его ID (icao24)"""
        pass


class SkyMapCoordinator(BaseSkyMapCoordinator, OpenApiIntegrator):
    """Получение и обработка данных с OpenStreetMap и OpenSky"""

    def __init__(self) -> None:
        super().__init__()

    def extraction_countries(self) -> Any:
        """Получения списка стран"""

        # Передаем запрос  через POST
        data = self.get_countries_checklist()

        search_index = {}
        for element in data.get("elements", []):
            tags = element.get("tags", {})
            iso_code = tags.get("ISO3166-1:alpha2") or tags.get("ISO3166-1")

            name_ru = tags.get("name:ru")
            name_en = tags.get("name:en") or tags.get("name")

            if iso_code:
                # Данные о стране
                country_data = {"iso_code": iso_code, "name_ru": name_ru, "name_en": name_en}

                # Добавляем в индекс оба названия
                if name_ru:
                    search_index[name_ru.lower()] = country_data
                if name_en:
                    search_index[name_en.lower()] = country_data

        return search_index

    def extraction_border_country(self, country_name: str) -> Any:
        """Метод получения коордиант - кортедж (широта, долгота) по коду страны"""

        data = self.get_border_country(country_name)

        # Проверяем, что пришел не пустой список
        if isinstance(data, list) and len(data) > 0:
            first_result = data[0]
            bbox = first_result.get("boundingbox", [])

            if len(bbox) == 4:
                # Nominatim отдает: [southLat, northLat, westLon, eastLon]
                # Превращаем в числа
                lat_min, lat_max, lon_min, lon_max = [float(x) for x in bbox]

                if lon_min == -180.0 and lon_max == 180.0:
                    if country_name == "Russia":
                        lon_min, lon_max = 19.0, 170.0  # Примерные границы РФ без разрыва меридиана
                    if country_name == "United States":
                        lon_min, lon_max = -130.0, -60.0  # Только материковая часть США

                # Возвращаем словарь, который удобно распаковать в параметры запроса
                return {
                    "lamin": lat_min,
                    "lamax": lat_max,
                    "lomin": lon_min,
                    "lomax": lon_max,
                }

        return {}

    def extraction_aircraft_info(self, border: dict[str, float]) -> Any:
        """Метод получения данных о самолетах над определенной рамкой"""

        data = self.get_os_info(border)
        return data
