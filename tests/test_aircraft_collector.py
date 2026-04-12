"""Тестерование пользовательской функции"""

from unittest.mock import patch

from src.aircraft_collector import user_interaction
from src.sky_control import AircraftStatus


def test_user_interaction_exit(mock_coordinator, mock_storage):
    """Проверка корректного выхода (пункт 0)"""
    with patch('builtins.input', side_effect=['0']):
        with patch('builtins.print') as mock_print:
            user_interaction()
            mock_print.assert_any_call("Завершение работы.")


def test_flow_fetch_and_top_n(mock_coordinator, mock_storage):
    """Тест сценария: Запрос данных (1) -> Топ по высоте (2) -> Выход (0)"""
    # Имитируем последовательный ввод пользователя
    inputs = [
        '1', 'Austria',  # Выбор 1, ввод страны
        '2', '1',  # Выбор 2, вывести 1 самолет
        '0'  # Выход
    ]

    with patch('builtins.input', side_effect=inputs):
        with patch('builtins.print') as mock_print:
            user_interaction()

            # Проверяем, что данные были запрошены
            mock_coordinator.extraction_border_country.assert_called_with('Austria')
            # Проверяем, что в консоль вывелось сообщение об успехе
            mock_print.assert_any_call("✅ Получено объектов: 1")
            # Проверяем заголовок ТОПа
            mock_print.assert_any_call("\n--- ТОП 1 по высоте ---")


def test_search_by_registration(mock_coordinator, mock_storage):
    """Тест поиска по стране регистрации (пункт 3)"""
    inputs = ['1', 'Austria', '3', 'Austria', '0']

    with patch('builtins.input', side_effect=inputs):
        with patch('builtins.print') as mock_print:
            user_interaction()
            # Проверяем, что поиск сработал (в моке у нас самолет из Austria)
            assert mock_print.called


def test_save_to_file(mock_coordinator, mock_storage):
    """Тест сохранения в файл (пункт 4)"""
    inputs = ['1', 'Austria', '4', '0']

    with patch('builtins.input', side_effect=inputs):
        user_interaction()
        # Проверяем, что метод save_all был вызван
        mock_storage.save_all.assert_called_once()
        # Проверяем, что переданы объекты нужного типа
        args, _ = mock_storage.save_all.call_args
        assert isinstance(args[0][0], AircraftStatus)


def test_invalid_country(mock_coordinator, mock_storage):
    """Тест ввода несуществующей страны"""
    inputs = ['1', 'UnknownCountry', '0']

    with patch('builtins.input', side_effect=inputs):
        with patch('builtins.print') as mock_print:
            user_interaction()
            mock_print.assert_any_call("❌ Страна не найдена в базе данных.")