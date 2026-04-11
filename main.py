"""Точка входа"""

from src.base import SkyMapCoordinator

if __name__ == "__main__":

    country_name = input("Введите название страны: ")
    fly_obj = SkyMapCoordinator()
    #print(fly_obj.extraction_countries_list)
    country_code = fly_obj.extraction_countries_list[country_name]
    print(f"Код для страны {country_name}: {country_code}")
    print(fly_obj.extraction_border_country(f"Рамка для страны: {country_name}"))
    # print(f"Данные о самолетах над страной {country_name}")
    # print(fly_obj.extraction_aircraft_info())
