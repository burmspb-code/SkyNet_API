"""Парсинг параметров подключения в словарь"""

from configparser import ConfigParser


def config_db(filename: str ="database.ini", section: str ="postgres") -> dict:
    """Создание словаря с параметрами подключения"""
    # Создание парсера
    parser = ConfigParser()
    parser.read(filename) # Чтение параметров
    db = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            db[param[0]] = param[1]
    else:
        raise Exception (f"Section {section} is not found in the file {filename}")

    return db
