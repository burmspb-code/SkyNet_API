# Проект SkyNet (Курсовая робата).

## Цель проекта:

***Разработка приложения, которое будет собирать информацию о самолетах в воздушных пространствах тех стран, которые выберет
пользователь, с дальнейшей обработкой полученных данных..***

**Инструкция по установке:**

Для работы проекта требуется [Poetry](https://python-poetry.org/).

    1. Клонируйте репозиторий:
      https://github.com/burmspb-code/SkyNet_API.git
    2. Установите зависимости:
        poetry install
    3. Запустите проект:
        poetry run python src/main.py

## 🧪 Тестирование:

Для проверки корректности работы модулей SkyNet используется фреймворк pytest.
Тесты покрывают основные функции загрузки, фильтрации и обработки данных.

Проверяемые модули: api_adapter.py, logging_config.py, token_open_sky.py, aircraft_collector.py,
base.py, depot.py, sky_control.py.

После запуска pytest --cov=src --cov-report=html подробный отчет доступен в папке htmlcov/index.html

**Используемые модули:**

    - api_adapter.py,
    - logging_config.py,
    - token_open_sky.py,
    - aircraft_collector.py,
    - base.py,
    - depot.py,
    - sky_control.py,
    - main.

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

### **main.py**

Точка входа в проект
