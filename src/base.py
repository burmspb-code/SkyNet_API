"""Описние базовых классов проекта"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Optional

from src.utils.api_adapter import OpenApiIntegrator


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
    """Получение и обработка данных с OpenStreetMap и OpenSky"""

    def __init__(self) -> None:
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

@dataclass(order=True)
class AircraftStatus:
    """Класс текущего состояния самолета"""

    # Поля для сравнения (первые в списке)
    velocity: Optional[float] = field(compare=True)
    baro_altitude: Optional[float] = field(compare=True)

    # Остальные поля не учавствуют в сравнении
    icao24: str = field(compare=False)
    callsign: str = field(compare=False)
    origin_country: str = field(compare=False)
    time_position: Optional[int] = field(compare=False)
    last_contact: Optional[int] = field(compare=False)
    longitude: Optional[float] = field(compare=False)
    latitude: Optional[float] = field(compare=False)
    on_ground: bool = field(compare=False)
    true_track: Optional[float] = field(compare=False)  # курс
    vertical_rate: Optional[float] = field(compare=False)
    sensors: Optional[list] = field(compare=False)
    geo_altitude: Optional[float] = field(compare=False)
    squawk: Optional[str] = field(compare=False)
    spi: bool = field(compare=False)
    position_source: int = field(compare=False)

    def __repr__(self):
        return f"<Plane {self.callsign} [{self.icao24}] Alt: {self.altitude}m>"
