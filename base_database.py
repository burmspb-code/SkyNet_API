"""Классы для работы с БД"""
import os

import psycopg2
from dotenv import load_dotenv

load_dotenv()
BD_SECRET = os.getenv("BD_SECRET")


class DBManager:
    """Класс для взаимодествия с БД Supabase"""

    def __init__(self):
        self.db_params = {
            "host": "aws-0-eu-west-1.pooler.supabase.com",
            "port": "5432",
            "database": "postgres",
            "user": "postgres.juafgoxrmbsgtcapwgqm",
            "password": BD_SECRET
        }
        self.conn = psycopg2.connect(**self.db_params)
        self.conn.autocommit = True  # Чтобы данные сохранялись сразу

    def save_country_dict_all(self, country_list: dict) -> None:
        """Сохранение справочной информации о названиях стран RU/ENG и кодов iso"""
        query = """
        INSERT INTO country_info (iso_code, name_ru, name_en)
        VALUES (%s, %s, %s)
        ON CONFLICT (iso_code) DO NOTHING;
        """
        with self.conn.cursor() as cursor:
            for country in country_list:
                cursor.execute(query, (country["iso_code"],
                                       country["name_ru"],
                                       country["name_en"]))



    def save_aircraft_country(self, country_iso: str) -> None:
        """Сохранение информации о воздушных судах в заданной стране"""
        pass

    def clear_aircraft_table(self) -> None:
        """Очистка таблицы с информацией о воздушных судах"""
        pass

    def get_countries_and_aeroplanes_count(self) -> list[tuple]:
        """Получает список всех стран и количество самолетов в их воздушных пространствах"""
        pass

    def get_all_aeroplanes(self, country_iso: str) -> list:
        """Получает список всех воздушных судов"""
        pass

    def get_avg_speed(self, country_iso: str) -> float:
        """Получает среднюю скорость по самолетам"""
        pass

    def get_aeroplanes_with_higher_speed(self, country_iso: str) -> list:
        """Получает список всех самолетов, у которых скорость выше средней"""
        pass

    def get_aeroplanes_with_keyword(self, country_iso: str, keyword: str) -> list:
        """Получает список всех самолетов, в позывном которых содержатся переданные в метод символы"""
        pass
