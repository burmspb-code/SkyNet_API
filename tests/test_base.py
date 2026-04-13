"""Тестирование базовой логики"""

from unittest.mock import patch, PropertyMock

from src.base import SkyMapCoordinator


def test_extraction_countries_indexing(coordinator):
    """Проверка создания индекса стран (RU/EN)"""
    mock_data = {
        'elements': [{
            'tags': {
                'ISO3166-1:alpha2': 'AT',
                'name:ru': 'Австрия',
                'name:en': 'Austria'
            }
        }]
    }

    # Патчим метод, который вызывается ВНУТРИ свойства extraction_countries
    with patch.object(SkyMapCoordinator, 'get_countries_checklist') as mock_get:
        mock_get.return_value = mock_data

        index = coordinator.extraction_countries()

        # Проверяем наличие ключей
        assert 'австрия' in index, f"Ключ 'австрия' не найден. Доступные ключи: {list(index.keys())}"
        assert index['австрия']['iso'] == 'AT'
        assert index['austria']['iso'] == 'AT'





def test_extraction_border_country_format(coordinator):
    """Проверка парсинга bbox от Nominatim"""
    mock_nominatim = [{
        'boundingbox': ['46.3', '49.0', '9.5', '17.1']
    }]
    with patch.object(SkyMapCoordinator, 'get_border_country', return_value=mock_nominatim):
        result = coordinator.extraction_border_country("Austria")
        assert result['lamin'] == 46.3
        assert result['lomax'] == 17.1






