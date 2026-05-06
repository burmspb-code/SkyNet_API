"""Модуль для тестирования функционала работы с БД"""

from dataclasses import asdict

import pandas as pd
from sqlalchemy import create_engine  # Для корректной работы pandas c postgres

from src.base import SkyMapCoordinator
from src.base_database import DBManager
from src.sky_control import AircraftStatus
from src.utils.config_db import config_db

pd.set_option('display.max_columns', None)  # Отображаются все столбцы

params = config_db()  # Параметры подключения
# Собираем строку
db_url = f"postgresql://{params['user']}:{params['password']}@{params['host']}:{params['port']}/{params['database']}"
# Подключаем движок
engine = create_engine(db_url)


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
    """Разворачиваем словари по коду"""
    return {
        item['iso_code']: {
            'name_ru': item['name_ru'],
            'name_en': item['name_en']
        }
        for item in data
    }


def extraction_data(query: str) -> pd.DataFrame:
    """Ивлечение таблицы из БД в датафрейм"""
    return pd.read_sql(query, engine)


def functional_testing() -> None:
    """Проверка работоспособности модулей работы с БД"""
    # Создаем объекты
    aircraft_obj = SkyMapCoordinator()
    aircraft_db = DBManager()

    # Очищаем таблицу с самолетами при старте приложения (опционально)
    aircraft_db.clear_table("aircraft_info")

    # Задаем список iso кодов стран для поиска самолетов
    list_iso_code_countries = ["RU", "UA", "TR", "FI", "US", "UY", "DE", "CN", "IT", "KZ"]

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
                border_country = aircraft_obj.extraction_border_country(country_name)  # Получаем рамку
                if border_country:
                    info = aircraft_obj.extraction_aircraft_info(border_country)  # Получаем инфо о самолетах
                    if info.get("states"):
                        aircraft_list = []
                        for s in info["states"]:
                            # Создаем объект (он сам отберет нужные 5 полей из 17)
                            status_obj = AircraftStatus(*s)

                            # Превращаем объект в словарь
                            aircraft_dict = asdict(status_obj)

                            # Добавляем ISO код страны, в которой мы сейчас ищем
                            aircraft_dict["country_iso_code"] = iso
                            aircraft_list.append(aircraft_dict)

                        # Передаем в базу список чистых словарей
                        aircraft_db.save_aircraft_country(aircraft_list)
                        print(f"Информация о самолетах по стране {country_name} ({iso}) добавлена")
                else:
                    print(f"Границы для страны {country_name} ({iso}) не найдены")
        else:
            print(f"Страна с кодом {iso} не найдена")

    # ПРОВЕРКА
    # Выводим данные из таблицы-справочника кодов на экран
    query = "SELECT * FROM iso_code_countries"
    print("\nДанные таблицы-справочника кодов:")
    print(extraction_data(query).head(5))

    # Выводим данные из таблицы о самолетах на экран
    query = "SELECT * FROM aircraft_info"
    print("\nДанные таблицы по самолетам:")
    print(extraction_data(query).head(5))

    # Выводим количество самолетов в заданной стране
    data = aircraft_db.get_countries_and_aeroplanes_count("RU")
    df = pd.DataFrame(data)
    print("\nКоличество самолетов в стране:")
    print(df)

    # Выводим количество самолетов во всех странах для поиска
    data = aircraft_db.get_countries_and_aeroplanes_count()
    df = pd.DataFrame(data)
    print("\nКоличество самолетов во всех странах:")
    print(df)

    # Выводим список всех воздушных судов в заданной стране
    data = aircraft_db.get_all_aeroplanes("RU")
    df = pd.DataFrame(data)
    print("\nСписок воздушных судов в стране:")
    print(df)

    # Выводим среднюю скорость по самолетам в заданной стране
    data = aircraft_db.get_avg_speed("RU")
    df = pd.DataFrame(data)
    print("\nСредняя скорость по самолетам в стране:")
    print(df)

    # Выводим список всех самолетов, у которых скорость выше средней в заданной стране
    data = aircraft_db.get_aeroplanes_with_higher_speed("RU")
    df = pd.DataFrame(data)
    print("\nСредняя скорость по самолетам выше средней в стране:")
    print(df)

    # Выводим список всех самолетов, в позывном которых содержатся переданные в метод символы в заданной стране
    keyword = "BAW"
    data = aircraft_db.get_aeroplanes_with_keyword("RU", keyword)
    df = pd.DataFrame(data)
    print(f"\nСписок самолетов с символами {keyword} в позывном в стране:")
    print(df)


if __name__ == '__main__':
    functional_testing()
