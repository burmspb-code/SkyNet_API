"""Точка входа"""

from src.base import SkyMapCoordinator

if __name__ == "__main__":

    fly_obj = SkyMapCoordinator()
    print(fly_obj.extraction_countries_list)
    print(fly_obj.extraction_border_country("Австрия"))
