"""Тестирование модуля для настройки логирования проекта"""

import logging
import os
from unittest.mock import patch

import pytest

from src.utils.logging_config import LOG_DIR, setup_logger


@pytest.fixture(autouse=True)
def cleanup_loggers():
    """Очистка логеров перед каждым тестом, чтобы они не кэшировались."""
    yield
    root_logger = logging.getLogger()
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    # Удаляем специфичные логеры, созданные в тестах
    logging.Logger.manager.loggerDict.clear()


def test_setup_logger_creates_directory():
    """Проверка, что папка для логов создается автоматически."""
    with patch("os.makedirs") as mock_makedirs:
        with patch("os.path.exists", return_value=False):
            setup_logger("test_dir_creator")
            mock_makedirs.assert_called_once_with(LOG_DIR)


def test_setup_logger_returns_correct_logger():
    """Проверка, что возвращается объект Logger с нужным именем и уровнем."""
    name = "test_logger"
    logger = setup_logger(name)

    assert isinstance(logger, logging.Logger)
    assert logger.name == name
    assert logger.level == logging.DEBUG


def test_setup_logger_adds_file_handler():
    """Проверка, что к логеру привязан FileHandler с правильным путем."""
    name = "file_test"
    logger = setup_logger(name)

    # Проверяем, что handler добавлен
    assert len(logger.handlers) == 1
    handler = logger.handlers[0]
    assert isinstance(handler, logging.FileHandler)

    # Проверяем путь к файлу (должен заканчиваться на имя_логера.log)
    expected_path = os.path.join(LOG_DIR, f"{name}.log")
    assert os.path.abspath(handler.baseFilename) == os.path.abspath(expected_path)


def test_prevent_duplicate_handlers():
    """Проверка, что повторный вызов setup_logger не добавляет лишних обработчиков."""
    name = "duplicate_test"
    logger1 = setup_logger(name)
    logger2 = setup_logger(name)

    assert logger1 is logger2
    assert len(logger2.handlers) == 1


def test_logger_writes_to_file(tmp_path):
    """Интеграционный тест: проверяем, что сообщение реально записывается в файл."""
    # Переопределяем LOG_DIR для теста через mock
    test_log_dir = tmp_path / "logs"
    with patch("src.utils.logging_config.LOG_DIR", str(test_log_dir)):
        logger = setup_logger("write_test")
        test_message = "Hello, OpenSky!"
        logger.debug(test_message)

        # Закрываем handler, чтобы файл записался на диск
        for h in logger.handlers:
            h.close()

        log_file = test_log_dir / "write_test.log"
        assert log_file.exists()
        content = log_file.read_text(encoding="utf-8")
        assert test_message in content
        assert "DEBUG" in content
