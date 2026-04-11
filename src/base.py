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
    def extraction_aircraft_info(self):
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
            name = tags.get('name:ru') or tags.get('name')  # Пытаемся взять русское название
            iso_code = tags.get('ISO3166-1')

            if name and iso_code:
                countries[iso_code] = name

        # Сортируем по названию для удобства
        return dict(sorted(countries.items(), key=lambda item: item[1]))

    def extraction_border_country(self, country_name: str) -> Any:
        """Метод получения коордиант - кортедж (широта, долгота) по коду страны"""

        data = self.get_border_country(country_name)

        # Проверяем, что пришел не пустой список
        if isinstance(data, list) and len(data) > 0:
            # Берем первый (самый релевантный) результат
            first_result = data[0]

            bbox = first_result.get('boundingbox', [])

            if len(bbox) == 4:
                # Превращаем строки в числа для дальнейшей работы
                return [float(x) for x in bbox]

        print(f"Данные для {country_name} не найдены.")
        return None

    def extraction_aircraft_info(self) -> Any:
        """Метод получения данных о самолетах над определенной рамкой"""

        data = get_os_info()
        return data
