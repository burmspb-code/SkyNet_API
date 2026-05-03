"""Классы для работы с БД"""
import psycopg2
from psycopg2.extras import RealDictCursor


class DBManager:
    """Класс для взаимодествия с БД Supabase, где
    db_params:Host, Database, User, Password, Port
    """

    def __init__(self, db_params: dict):
        self.conn = psycopg2.connect(**db_params)
        self.conn.autocommit = True  # Чтобы данные сохранялись сразу

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
