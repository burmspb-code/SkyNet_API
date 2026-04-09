import requests

from src.utils.logging_config import setup_logger

logger = setup_logger("HttpClient")

class HttpClientMixin:
    """Примесь для выполнения http запросов"""

    def _post(self, url: str, data: dict = None) -> dict:
        headers = {
            'User-Agent': 'SkyNetTest/1.0',
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        # Инициализируем переменную заранее
        response = None

        logger.info(f"Отправка POST запроса на {url}")

        try:
            response = requests.post(url, data=data, headers=headers, timeout=60)
            logger.info(f"Статус ответа: {response.status_code}")
            response.raise_for_status()
            return response.json()

        except JSONDecodeError:
            logger.error(f"Ошибка парсинга JSON. Получен HTML/текст: {response.text[:200]}...")
            return {}

        except RequestException as e:
            # Логируем сетевые ошибки (504, 404, Connection Error и т.д.)
            logger.error(f"Сетевая ошибка при запросе к {url}: {e}")
            if hasattr(e, 'response') and e.response is not None:
                logger.debug(f"Тело ошибки: {e.response.text}")
            return {}
        except Exception as e:
            logger.critical(f"Непредвиденная ошибка: {e}")
            return {}