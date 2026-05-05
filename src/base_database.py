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
    """Класс для взаимодествия с БД PostgresSQL"""

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

    def save_aircraft_country(self, country_iso: str) -> None:
        """Сохранение информации о воздушных судах в заданной стране"""

        self.insert_data("aircraft_info", country_iso, conflict_column="icao24")

    def save_countries_all(self, countries_list: list[dict]) -> None:
        """Сохранение справочной информации о названиях стран RU/ENG и кодов iso"""

        with self.conn.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM iso_code_countries")  # Считаем колдичество строк
            count = cursor.fetchone()[0]

        # Если справочник не полон (или пуст) обновляем
        if len(countries_list) > count:
            self.insert_data("iso_code_countries", countries_list, conflict_column="iso_code")

    def _execute(self, query: str, params: tuple = None) -> list[tuple]:
        """Внутренний метод для безопасного выполнения любого запроса"""
        try:
            with self.conn.cursor() as cursor:
                cursor.execute(query, params)
                return cursor.fetchall()
        except errors.ProgrammingError as e:
            self.conn.rollback()
            print(f"Синтаксическая ошибка в SQL: {e}")
        except errors.OperationalError as e:
            self.conn.rollback()
            print(f"Ошибка соединения с БД: {e}")
        except Exception as e:
            self.conn.rollback()
            print(f"Произошла системная ошибка: {e}")
        return []

    def get_iso_code(self, country_name: str) -> str | None:
        """Получение iso кода по названию страны из таблицы-справочника"""

        query = """SELECT iso_code FROM iso_code_countries
                WHERE name_ru ILIKE %s OR name_en ILIKE %s
                LIMIT 1;
        """

        return self._execute(query, (country_name, country_name))

    def clear_table(self, table_name: str) -> None:
        """Безопасная очистка таблицы"""

        query = sql.SQL("TRUNCATE TABLE {} RESTART IDENTITY CASCADE;").format(sql.Identifier(table_name))
        with self.conn.cursor() as cursor:
            cursor.execute(query)

    def get_countries_and_aeroplanes_count(self, country_iso: str = None) -> list[tuple]:
        """Получает список всех стран и количество самолетов в их воздушных пространствах"""

        # Базовый запрос
        query = """
        SELECT country_iso_code, COUNT(icao24) as airplane_count
        FROM aircraft_info
        """
        # Если есть код, то фильтруем по коду, если нет то берем все значения
        if country_iso:
            query += " WHERE country_iso_code=%s"
            params = (country_iso,)
        else:
            params = None
        # Группировка + сортировка по возрастанию
        query += " GROUP BY country_iso_code ORDER BY airplane_count DESC;"

        return self._execute(query, params)

    def get_all_aeroplanes(self, country_iso: str) -> list[tuple]:
        """Получает список всех воздушных судов"""
        query = """
        SELECT icao24
        FROM aircraft_info
        WHERE country_iso_code=%s
        ORDER BY icao24;
        """

        return self._execute(query, (country_iso,))

    def get_avg_speed(self, country_iso: str) -> list[tuple]:
        """Получает среднюю скорость по самолетам"""
        query = """
        SELECT AVG(velocity)
        FROM aircraft_info
        WHERE country_iso_code=%s
        """

        return self._execute(query, (country_iso,))

    def get_aeroplanes_with_higher_speed(self, country_iso: str) -> list:
        """Получает список всех самолетов, у которых скорость выше средней"""
        query = """
        SELECT icao24, velocity
        FROM aircraft_info
        WHERE country_iso_code=%s AND velocity > (
          SELECT AVG(velocity)
          FROM aircraft_info
          WHERE country_iso_code=%s
          )
        ORDER BY velocity DESC;
        """

        return self._execute(query, (country_iso, country_iso))

    def get_aeroplanes_with_keyword(self, country_iso: str, keyword: str) -> list:
        """Получает список всех самолетов, в позывном которых содержатся переданные в метод символы"""
        query = """
        SELECT icao24, callsign
        FROM aircraft_info
        WHERE country_iso_code=%s AND callsign LIKE %s
        ORDER BY callsign
        """

        # Чтобы найти слово ВНУТРИ строки, его нужно окружить знаками %
        # Например: '%AF%' найдет 'AFL123', 'BAF44' и т.д.
        search_pattern = f"%{keyword}%"

        return self._execute(query, (country_iso, search_pattern))
