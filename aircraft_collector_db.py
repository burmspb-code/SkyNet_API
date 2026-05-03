"""Модуль взаимодествия с пользователем с ипользованием БД"""
from psycopg2.extras import RealDictCursor

from base_database import DBManager
from src.base import SkyMapCoordinator


def user_interaction_bd() -> None:
    """Функция для взаимодествия с пользователем"""

    print("Отслеживание информации по воздушным судам будет вестись в четырёх странах: "
          "\n Россия(RUS), Украина(UKR), Турция(TUR), Финляндия(FIN)")

    # Получаем справочную информацию по всем страм
    fly_obj = SkyMapCoordinator()
    country_dict = fly_obj.extraction_countries()

    # Список заданных пользователем кодов стран для отслеживания
    user_country_iso_list = ["RUS", "UKR", "TUR", "FIN"]

    aircraft_db = DBManager()

    results = {}
    # Проверка пустых таблиц
    with aircraft_db.conn.cursor(cursor_factory=RealDictCursor) as cur:
        # Проверяем таблицу стран
        cur.execute("SELECT * FROM country_info")
        results['countries'] = cur.fetchall()

    print(results)

if __name__ == '__main__':
    user_interaction_bd()
