"""Основной модуль связующей логикми для получения информации о самолетах в заданном регионе"""

from src.base import SkyMapCoordinator

"""
1. Нужно получить рамку страны по входному country_name.
2. Нужно отправить запрос на сервис OpenSky по заданной рамке и получить ответ JSON.
3. Нужно обработать ответ и получить дынные в соответсвующем формате.
"""
fly_obj = SkyMapCoordinator() # Создаем рабочий объект для работы с сервисами OpenStreetMap и OpenSky
country_dict = fly_obj.extraction_countries_list # Получаем словарь со странами

if country_dict:
    while  True:
        country_name = input("Введите название страны: ")
        country_code = country_dict.get(country_name, None) # Получаем код страны из словаря
        if country_code:
            print(f"Код для страны {country_name}: {country_code}")
            border_country = fly_obj.extraction_border_country(country_name)
            if border_country:
                print(f"Рамка для страны {country_name}: {border_country}")
                aircraft_info = fly_obj.extraction_aircraft_info(border_country)
                print(aircraft_info)
                break
            else:
                print("Ошибка. Такой рамки нет. Повторите попытку")
        else:
            print("Такой страны нет в OpenStreetMap")

