"""Тестирование модулья sky_control"""

from src.sky_control import AircraftStatus


def test_aircraft_status_validation():
    """Тест обработки "битых" данных от OpenSky API"""
    # 17 параметров, где есть None в высоте и странный тип в позывном
    raw_data = [
        None,
        12345,
        None,
        0,
        0,
        0,
        0,
        None,
        True,
        -100.5,
        0,
        0,
        0,
        0,
        0,
        False,
        0,
    ]

    status = AircraftStatus(*raw_data)

    assert status.callsign == "12345"  # Приведено к строке
    assert status.altitude == 0.0  # None заменен на 0.0
    assert status.velocity == 100.5  # Отрицательная скорость стала положительной
    assert status.on_ground is True  # Boolean корректен
