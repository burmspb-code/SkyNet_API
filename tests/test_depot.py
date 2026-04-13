"""Тестирование модуля depot"""

from src.depot import JsonAircraftStorage


def test_json_storage_lifecycle(tmp_path):
    """Интеграционный тест записи и чтения JSON"""
    file_path = tmp_path / "test_history.json"
    storage = JsonAircraftStorage(str(file_path))

    # Данные для сохранения
    sample_aircrafts = [
        {
            "icao24": "4bb0eb",
            "callsign": "AFL123",
            "altitude": 10000,
            "origin_country": "Russia",
        },
        {
            "icao24": "4007f4",
            "callsign": "BAW456",
            "altitude": 11000,
            "origin_country": "UK",
        },
    ]

    # 1. Тест сохранения
    storage.save_all(sample_aircrafts)

    # 2. Тест чтения
    loaded_data = storage._read_all()
    assert len(loaded_data) == 2
    assert loaded_data[0]["callsign"] == "AFL123"

    # 3. Тест поиска
    search_result = storage.get_aircraft({"origin_country": "UK"})
    assert len(search_result) == 1
    assert search_result[0]["callsign"] == "BAW456"


def test_json_storage_error_handling(tmp_path):
    """Тест поведения при битом JSON файле"""
    file_path = tmp_path / "broken.json"
    file_path.write_text("not a json")

    storage = JsonAircraftStorage(str(file_path))
    assert storage._read_all() == []  # Должен вернуть пустой список, а не упасть
