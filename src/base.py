"""Описние базовых классов проекта"""

import os
import json
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

        return {}

    def extraction_aircraft_info(self, border) -> Any:
        """Метод получения данных о самолетах над определенной рамкой"""

        data = self.get_os_info(border)
        return data


@dataclass(order=True)
class AircraftStatus:
    """Класс текущего состояния самолета"""

    # Поля для сравнения
    velocity: float = field(compare=True)
    altitude: float = field(compare=True)

    # Информационные поля
    callsign: str = field(compare=False)
    origin_country: str = field(compare=False)
    on_ground: bool = field(compare=False)

    def __init__(self, *args):
        """Принимает все 17 параметров от API, но сохраняет только 5"""
        # Индексы в данных OpenSky:
        # 1: callsign, 2: country, 7: baro_altitude, 8: on_ground, 9: velocity

        # Валидация позывного (индекс 1)
        raw_callsign = args[1]
        self.callsign = str(raw_callsign).strip() if raw_callsign else "Н/Д"

        # Валидация страны (индекс 2)
        self.origin_country = str(args[2]) if args[2] else "Неизвестно"

        # Валидация высоты (индекс 7)
        raw_alt = args[7]
        if raw_alt is None:
            self.altitude = 0.0
        elif not isinstance(raw_alt, (int, float)):
            raise ValueError(f"Некорректный тип высоты: {type(raw_alt)}")
        else:
            self.altitude = float(raw_alt)

        # Валидация статуса земли (индекс 8)
        self.on_ground = bool(args[8])

        # Валидация скорости (индекс 9)
        raw_vel = args[9]
        if raw_vel is None:
            self.velocity = 0.0
        elif raw_vel < 0:
            # Технически скорость относительно земли не может быть < 0
            self.velocity = abs(float(raw_vel))
        else:
            self.velocity = float(raw_vel)

    def __repr__(self):
        status = "🅿️ На земле" if self.on_ground else "✈️ В воздухе"
        return (f"{status} | Рейс: {self.callsign} ({self.origin_country}) | "
                f"Высота: {int(self.altitude)}м | Скорость: {int(self.velocity * 3.6)}км/ч")


class JsonAircraftStorage(AircraftStorage):
    def __init__(self, filename: str = "aircrafts.json"):
        self.filename = filename
        # Создаем пустой файл, если его нет
        if not os.path.exists(self.filename):
            with open(self.filename, 'w', encoding='utf-8') as f:
                json.dump([], f)

    def _read_all(self) -> list:
        try:
            # Проверяем размер файла: если 0, возвращаем пустой список
            if os.path.getsize(self.filename) == 0:
                return []

            with open(self.filename, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            # Если файла нет или в нем "мусор", тоже возвращаем пустой список
            return []

    def _write_all(self, data: list):
        with open(self.filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    def add_aircraft(self, aircraft: dict):
        data = self._read_all()
        # Проверяем, нет ли уже такого самолета (по icao24)
        data = [item for item in data if item.get('icao24') != aircraft.get('icao24')]
        data.append(aircraft)
        self._write_all(data)
        print(f"✅ Самолет {aircraft.get('callsign')} сохранен в JSON.")

    def get_aircraft(self, criteria: dict) -> list:
        data = self._read_all()
        results = []
        for item in data:
            # Проверяем совпадение по всем переданным критериям
            if all(item.get(k) == v for k, v in criteria.items()):
                results.append(item)
        return results

    def delete_aircraft(self, icao24: str):
        data = self._read_all()
        new_data = [item for item in data if item.get('icao24') != icao24]
        if len(data) != len(new_data):
            self._write_all(new_data)
            print(f"🗑️ Самолет с ICAO {icao24} удален.")
        else:
            print(f"❌ Самолет с ICAO {icao24} не найден.")


    def save_all(self, aircraft_list: list):
        """Сохраняет весь список объектов за один раз"""
        existing_data = self._read_all()

        # Превращаем объекты dataclass в словари, если это еще не сделано
        new_entries = []
        for ac in aircraft_list:
            if hasattr(ac, '__dict__'):
                new_entries.append(ac.__dict__)
            else:
                new_entries.append(ac)

        # Объединяем старые и новые данные (можно добавить логику исключения дубликатов)
        total_data = existing_data + new_entries

        self._write_all(total_data)
        print(f"✅ Успешно сохранено новых записей: {len(new_entries)}")