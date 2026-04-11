"""Основной модуль связующей логикми для получения информации о самолетах в заданном регионе"""

from src.base import SkyMapCoordinator, AircraftStatus, JsonAircraftStorage


def user_interaction():
    """Функция для взаимодествия с пользователем"""
    fly_obj = SkyMapCoordinator()
    storage = JsonAircraftStorage("history.json")
    country_dict = fly_obj.extraction_countries_list

    # Вспомогательный список для хранения результатов последнего запроса в памяти
    current_aircrafts = []

    print("--- Система мониторинга воздушного пространства ---")

    while True:
        print("\nДоступные действия:")
        print("1. Запросить данные по стране (OpenSky)")
        print("2. Топ N самолетов по высоте")
        print("3. Поиск самолетов по стране регистрации (в текущем списке)")
        print("4. Сохранить текущий список в файл")
        print("0. Выход")

        choice = input("\nВыберите действие: ")

        if choice == "1":
            country_name = input("Введите название страны (напр. Австрия): ")
            if country_name in country_dict:
                border = fly_obj.extraction_border_country(country_name)
                info = fly_obj.extraction_aircraft_info(border)

                if info.get('states'):
                    current_aircrafts = [AircraftStatus(*s) for s in info['states']]
                    print(f"✅ Получено объектов: {len(current_aircrafts)}")
                else:
                    print("⚠️ В этом регионе сейчас нет самолетов.")
            else:
                print("❌ Страна не найдена в базе данных.")

        elif choice == "2":
            if not current_aircrafts:
                print("⚠️ Сначала получите данные (пункт 1).")
                continue

            try:
                n = int(input("Сколько самолетов вывести? (N): "))
                # Сортируем по высоте (благодаря order=True в dataclass)
                top_n = sorted(current_aircrafts, key=lambda x: x.altitude, reverse=True)[:n]
                print(f"\n--- ТОП {n} по высоте ---")
                for p in top_n:
                    print(p)
            except ValueError:
                print("❌ Введите число.")

        elif choice == "3":
            if not current_aircrafts:
                print("⚠️ Список пуст.")
                continue

            search_country = input("Введите страну регистрации: ")
            filtered = [p for p in current_aircrafts if p.origin_country.lower() == search_country.lower()]

            if filtered:
                for p in filtered: print(p)
            else:
                print("Ничего не найдено.")


        elif choice == "4":
            if not current_aircrafts:
                print("⚠️ Нечего сохранять.")
                continue

            # Сохраняем весь список разом
            storage.save_all(current_aircrafts)

        elif choice == "0":
            print("Завершение работы.")
            break
        else:
            print("Некорректный ввод.")

if __name__ == "__main__":
    user_interaction()