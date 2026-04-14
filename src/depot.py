"""Модуль для работы с файлами/базами данных"""

import json
import os
from dataclasses import asdict, is_dataclass

from src.base import AircraftStorage
from src.utils.logging_config import setup_logger

logger = setup_logger("depot")


class JsonAircraftStorage(AircraftStorage):
    """Класс для работы с файлами в формате JSON"""

    def __init__(self, filename: str = "aircrafts.json"):

        # Идем на уровень выше
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        data_dir = os.path.join(base_dir, "data")

        # Создаем папку, если её нет
        os.makedirs(data_dir, exist_ok=True)

        # Сохраняем полный путь к файлу в приватный атрибут
        self.__filename = os.path.join(data_dir, filename)

        # Создаем пустой файл, если он не существует
        if not os.path.exists(self.__filename):
            with open(self.__filename, "w", encoding="utf-8") as f:
                json.dump([], f)

    @property
    def filename(self):
        """Геттер для безопасного чтения имени файла"""
        return self.__filename

    def _read_all(self) -> list:
        """Загрузка JSON файла"""
        try:
            # Проверяем размер файла: если 0, возвращаем пустой список
            if os.path.getsize(self.__filename) == 0:
                return []

            with open(self.__filename, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            logger.error("Файл не найден.")
            return []
        except json.JSONDecodeError:
            logger.error("Ошибка декодиирования JSON")
            return []

    def _write_all(self, data: list):
        """Запись данных JSON в файл"""

        # Конвертируем только объекты-датаклассы, остальное оставляем без изменений
        # C Проверкой not isinstance(obj, type)
        serializable_data = [
            asdict(obj) if is_dataclass(obj) and not isinstance(obj, type) else obj
            for obj in data
        ]

        with open(self.__filename, "w", encoding="utf-8") as f:
            json.dump(serializable_data, f, ensure_ascii=False, indent=4)

    def add_aircraft(self, aircraft: dict):
        """Добавление выбранного самолета"""
        data = self._read_all()
        # Проверяем, нет ли уже такого самолета (по icao24)
        data = [item for item in data if item.get("icao24") != aircraft.get("icao24")]
        data.append(aircraft)
        self._write_all(data)
        logger.info(f"✅ Самолет {aircraft.get('callsign')} сохранен в JSON.")

    def get_aircraft(self, criteria: dict) -> list:
        """Поиск по заданному критерию"""
        data = self._read_all()
        results = []
        for item in data:
            # Проверяем совпадение по всем переданным критериям
            if all(item.get(k) == v for k, v in criteria.items()):
                results.append(item)
        return results

    def delete_aircraft(self, icao24: str):
        """Удаление выбранного самолета"""
        data = self._read_all()
        new_data = [item for item in data if item.get("icao24") != icao24]
        if len(data) != len(new_data):
            self._write_all(new_data)
            logger.info(f"🗑️ Самолет с ICAO {icao24} удален.")
        else:
            logger.info(f"❌ Самолет с ICAO {icao24} не найден.")

    def save_all(self, aircraft_list: list):
        """Сохраняет список объектов, исключая дубликаты по icao24"""

        # Загружаем то, что уже есть в файле
        existing_data = self._read_all()

        # Создаем словарь для объединения (ключ — icao24)
        combined_data = {}

        if existing_data:
            combined_data = {
                item.get("icao24"): item for item in existing_data if item.get("icao24")
            }

        # Добавляем новые данные, заменяя старые при совпадении ID
        new_count = 0
        for ac in aircraft_list:
            # Приводим объект к словарю (учитывая __slots__ через asdict)
            if is_dataclass(ac) and not isinstance(ac, type):
                ac_dict = asdict(ac)
            elif hasattr(ac, "__dict__"):
                ac_dict = ac.__dict__
            else:
                ac_dict = ac

            icao = ac_dict.get("icao24")
            if icao:
                combined_data[icao] = ac_dict
                new_count += 1

        # Превращаем обратно в список и записываем
        self._write_all(list(combined_data.values()))

        logger.info(f"✅ Данные обновлены. Обработано новых записей: {new_count}")
