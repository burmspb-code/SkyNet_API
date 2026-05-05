"""Модуль взаимодествия с пользователем с ипользованием БД"""
import sys

from src.base import SkyMapCoordinator
from src.base_database import DBManager
from src.sky_control import AircraftStatus
from dataclasses import asdict

def user_interaction_bd() -> None:
    """Функция для взаимодествия с пользователем"""
    pass


def extracting_unique_records(row_index: dict) -> list[dict]:
    """Преобразование словаря в список словарей с уникальными значениями"""
    row_code_list = []
    iso_set = set()
    for item in row_index.values():
        _ = item.get("iso_code")
        if _ not in iso_set:
            row_code_list.append(item)
            iso_set.add(_)
    list_sorted = sorted(row_code_list, key=lambda x: x.get("iso_code"))
    return list_sorted


def get_country_lookup(data: list[dict]) -> dict:
    """Разворачиваем свлори по коду"""
    return {
        item['iso_code']: {
            'name_ru': item['name_ru'],
            'name_en': item['name_en']
        }
        for item in data
    }


def functional_testing() -> None:
    """Проверка работоспособности модулей"""
    # Создаем объекты
    aircraft_obj = SkyMapCoordinator()
    aircraft_db = DBManager()

    # Очищаем таблицу с самолетами при старте приложения (опционально)
    aircraft_db.clear_table("aircraft_info")

    # Задаем список iso кодов стран
    list_iso_code_countries = ["RU", "UA", "TR", "FI", "US", "FR", "DE", "CN", "IT", "KZ"]

    # Получение словаря со странами с ресурса OSM
    countries_dict = aircraft_obj.extraction_countries()

    # Преобразуем в список словарей
    countries_list = extracting_unique_records(countries_dict)
    lookup = get_country_lookup(countries_list)  # Разворачиваем для поиска по ключам (опционально)

    # Записываем countries_list в таблицу-справочник
    aircraft_db.save_countries_all(countries_list)

    # Получаем информацию о самолетах в заданном списке стран и заносим в БД
    for iso in list_iso_code_countries:
        country_data = lookup.get(iso)
        if country_data:
            country_name = country_data.get("name_en")
            if country_name:
                border_country = aircraft_obj.extraction_border_country(country_name)  # Получаеи рамку
                if border_country:
                    info = aircraft_obj.extraction_aircraft_info(border_country)  # Получаем инфо о самолетах
                    if info.get("states"):
                        aircraft_list = []
                        for s in info["states"]:
                            # Создаем объект (он сам отберет нужные 5 полей из 17)
                            status_obj = AircraftStatus(*s)

                            # Превращаем объект в словарь
                            aircraft_dict = asdict(status_obj)

                            # ВАЖНО: Добавляем ISO код страны, в которой мы сейчас ищем
                            aircraft_dict["country_iso_code"] = iso
                            aircraft_list.append(aircraft_dict)

                        # Теперь передаем в базу список чистых словарей
                        aircraft_db.save_aircraft_country(aircraft_list)
                        print(f"Информация о самолетах по стране {country_name} ({iso}) добавлена")
                else:
                    print(f"Границы для страны {country_name} ({iso}) не найдены")
        else:
            print(f"Страна с кодом {iso} не найдена")


if __name__ == '__main__':
    functional_testing()
