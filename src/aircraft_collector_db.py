"""Модуль взаимодествия с пользователем с ипользованием БД"""

from src.base_database import DBManager
from src.base import SkyMapCoordinator


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


def functional_testing() -> None:
    """Проверка работоспособности модулей"""
    # Создаем объекты
    aircraft_obj = SkyMapCoordinator()
    aircraft_db = DBManager()

    # Задаем список iso кодов стран
    list_iso_code_countries = ["RUS", "UKR", "TUR", "FIN", "USA", "FRA", "DEU", "CHN", "ITA", "KAZ"]

    # Получение словаря со странами с ресурса OSM
    countries_dict = aircraft_obj.extraction_countries()

    # Преобразуем в список словарей
    countries_list = extracting_unique_records(countries_dict)

    # Записываем countries_list в таблицу-справочник
    aircraft_db.save_countries_all(countries_list)








if __name__ == '__main__':
    functional_testing()
