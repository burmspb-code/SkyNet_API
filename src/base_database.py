"""Классы для работы с БД"""
import os

import psycopg2
from dotenv import load_dotenv
from psycopg2 import sql

load_dotenv()
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_DATABASE = os.getenv("DB_DATABASE")
DB_USER = os.getenv("DB_USER")
DB_SECRET = os.getenv("DB_SECRET")


class DBManager:
    """Класс для взаимодествия с БД Supabase"""

    def __init__(self):
        self.db_params = {
            "host": DB_HOST,
            "port": DB_PORT,
            "database": DB_DATABASE,
            "user": DB_USER,
            "password": DB_SECRET
        }
        self.conn = psycopg2.connect(**self.db_params)
        self.conn.autocommit = True  # Чтобы данные сохранялись сразу

    def insert_data(self, table_name: str, data: list[dict], conflict_column: str = None) -> None:
        """Общий метод записи данных в таблицу БД, где
        table_name - имя таблицы,
        data - список словарей с данными для записи,
        conflict_column - столбец с уникальными данными
        """
        if not data:
            return

        columns = data[0].keys()  # Получаем наименования столбцов

        # Преобразуем для INSERT в строковый формат
        columns_str = ", ".join(columns)
        placeholders = ", ".join([f"%({col})s" for col in columns])

        query = f"INSERT INTO {table_name} ({columns_str}) VALUES ({placeholders})"

        if conflict_column:
            update_columns = [f"{col}=EXCLUDED.{col}" for col in columns if col != conflict_column]
            if update_columns:
                update_str = ", ".join(update_columns)
                query += f" ON CONFLICT ({conflict_column}) DO UPDATE SET {update_str}"
            else:
                # Если обновлять нечего, просто ничего не делаем при конфликте
                query += f" ON CONFLICT ({conflict_column}) DO NOTHING"

        with self.conn.cursor() as cursor:
            cursor.executemany(query, data)

    def save_countries_all(self, countries_list: list[dict]) -> None:
        """Сохранение справочной информации о названиях стран RU/ENG и кодов iso"""

        with self.conn.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM iso_code_countries")  # Считаем колдичество строк
            count = cursor.fetchone()[0]

        # Если справочник не полон (или пуст) обновляем
        if len(countries_list) > count:
            self.insert_large_data("iso_code_countries", countries_list, conflict_column="iso_code")

    def get_iso_code(self, country_name: str) -> str | None:
        """Получение iso кода по названию страны из таблицы-справочника"""

        query = """SELECT iso_code FROM iso_code_countries
                WHERE name_ru ILIKE %s OR name_en ILIKE %s
                LIMIT 1;
        """
        with self.conn.cursor() as cursor:
            cursor.execute(query, (country_name, country_name))
            result = cursor.fetchone()

        return result[0] if result else None

    def save_aircraft_country(self, country_iso: str) -> None:
        """Сохранение информации о воздушных судах в заданной стране"""
        pass

    def clear_table(self, table_name: str) -> None:
        """Безопасная очистка таблицы"""

        query = sql.SQL("TRUNCATE TABLE {} RESTART IDENTITY CASCADE;").format(sql.Identifier(table_name))
        with self.conn.cursor() as cursor:
            cursor.execute(query)

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
