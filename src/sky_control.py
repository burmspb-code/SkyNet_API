"""Модуль для взаимодейсвия с воздушными судами"""

from dataclasses import dataclass, field

from src.utils.logging_config import setup_logger

logger = setup_logger("sky_control")


@dataclass(
    order=True, slots=True, init=False
)  # slots=True создает __slots__ автоматически
class AircraftStatus:
    """Класс текущего состояния самолета"""

    # Поля для сравнения
    velocity: float = field(compare=True)
    altitude: float = field(compare=True)

    # Информационные поля
    icao24: str = field(compare=False)
    callsign: str = field(compare=False)
    origin_country: str = field(compare=False)
    on_ground: bool = field(compare=False)

    def __init__(self, *args):
        """Принимает все 17 параметров от API, но сохраняет только 5"""
        # Индексы в данных OpenSky:
        # 0: icao24, 1: callsign, 2: country, 7: baro_altitude, 8: on_ground, 9: velocity

        # Валидация идентификатора борта (индекс 0)
        self.icao24 = str(args[0]) if args[0] else "Неизвестно"

        # Валидация позывного (индекс 1)
        raw_callsign = args[1]
        self.callsign = str(raw_callsign).strip() if raw_callsign else "Н/Д"

        # Валидация страны (индекс 2)
        self.origin_country = str(args[2]) if args[2] else "Неизвестно"

        # Валидация высоты (индекс 7)
        raw_alt = args[7]
        if raw_alt is None:
            self.altitude = 0.0
        elif not isinstance(raw_alt, (int, float)):
            logger.error(
                f"Некорректный тип высоты: {type(raw_alt)}, значение заменено на 0.0."
            )
            self.altitude = 0.0
        else:
            self.altitude = float(raw_alt)

        # Валидация статуса земли (индекс 8)
        self.on_ground = bool(args[8])

        # Валидация скорости (индекс 9)
        raw_vel = args[9]
        if raw_vel is None:
            self.velocity = 0.0
        elif raw_vel < 0:
            # Технически скорость относительно земли не может быть < 0
            self.velocity = abs(float(raw_vel))
        else:
            self.velocity = float(raw_vel)

    def __repr__(self):
        """Вывод информации для разработчкика"""
        status = "🅿️ На земле" if self.on_ground else "✈️ В воздухе"
        return (
            f"{status} | Рейс: {self.callsign} ({self.origin_country}) | "
            f"Высота: {int(self.altitude)}м | Скорость: {int(self.velocity * 3.6)}км/ч"
        )
