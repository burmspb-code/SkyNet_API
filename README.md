# Проект SkyNet (Курсовая робата).
Данной проект является дополнением к предыдущей работе, целью которого является занесение информации
с открытых ресурсов https://opensky-network.org/ и https://opensky-network.org/ в локальную базу данных PostgresSQL,
и работа с этими данными.


**Инструкция по установке:**

Для работы проекта требуется [Poetry](https://python-poetry.org/).

    1. Клонируйте репозиторий:
      https://github.com/burmspb-code/SkyNet_API.git
    2. Установите зависимости:
        poetry install
    3. Запустите проект:
        poetry run python src/main.py

Для работы проекта нужно создать три таблицы в БД PostgresSQL.
Скопируйте и запустите SQL-скрипт:

    Для таблицы "iso_code_countries":

    create table iso_code_countries(
    iso_code varchar(3) primary key,
    name_ru text,
    name_en text
    );

    Для таблицы "aircraft_info":

    create table aircraft_info(
    icao24 text primary key,
    country_iso_code varchar(3),
    velocity float8,
    altitude float8,
    callsign text,
    origin_country text,
    on_ground boolean,
    last_update_time timestamptz default now()
    );

    
    Для таблицы "countries_info":

    create table countries_info(
    iso_code varchar(3) primary key,
    lat_min float8,
    lat_max float8,
    lon_min float8,
    lon_max float8
    );

Проверка работы модулей - RUN  main.py

**Используемые модули:**

    - api_adapter.py,
    - logging_config.py,
    - token_open_sky.py,
    - aircraft_collector.py,
    - base.py,
    - depot.py,
    - sky_control.py,
    - main.

Модули для работы с БД:
    
    - config_db.py,
    - aircraft_collector_db.py,
    - base_database.py.

### **api_adapter**

Модуль для взаимодействия с API-сервисами OpenStreetMap и OpenSky"

### **logging_config**

Модуль настройки для логирования проекта

### **token_open_sky**

Модуль для получения токена для OpenSky

### **aircraft_collector**

Моудль для взаимодействия с пользователем через консоль

### **base.py**

Модуль с описнием базовых классов проекта

### **depot.py**

Модуль для работы с файлами/базами данных"

### **sky_control.py**

Модуль для взаимодейсвия с воздушными судами

### **config_db.py**

Модуль для парсинга параметров подключения в словарь

### **aircraft_collector_db.py**

Модуль для тестирования функционала работы с БД

### **base_database.py**

Модуль с описанием классов проекта для работы с БД

### **main.py**

Точка входа в проект
