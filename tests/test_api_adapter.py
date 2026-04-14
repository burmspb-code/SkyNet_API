import requests_mock


def test_safe_request_success(integrator):
    """Тест успешного выполнения запроса"""
    url = "https://test.com"
    payload = {"status": "ok"}

    with requests_mock.Mocker() as m:
        m.get(url, json=payload, status_code=200)
        result = integrator._safe_request("GET", url)
        assert result == payload


def test_safe_request_json_error(integrator):
    """Тест ошибки парсинга JSON (когда пришел HTML вместо JSON)"""
    url = "https://test.com"

    with requests_mock.Mocker() as m:
        m.get(url, text="<html>Error</html>", status_code=200)
        result = integrator._safe_request("GET", url)
        assert result == {}


def test_safe_request_http_error(integrator):
    """Тест сетевой ошибки (например, 404 или 500)"""
    url = "https://test.com"

    with requests_mock.Mocker() as m:
        m.get(url, status_code=404)
        result = integrator._safe_request("GET", url)
        assert result == {}


def test_get_countries_checklist(integrator):
    """Тест получения списка стран (POST запрос)"""
    mock_data = {"elements": [{"tags": {"name": "Russia"}}]}

    with requests_mock.Mocker() as m:
        m.post("https://overpass.openstreetmap.fr/api/interpreter", json=mock_data)
        result = integrator.get_countries_checklist()
        assert result == mock_data
        assert m.called


def test_get_border_country(integrator):
    """Тест получения границ страны (GET запрос)"""
    country = "France"
    mock_response = [{"lat": "46.2", "lon": "2.2"}]

    with requests_mock.Mocker() as m:
        m.get("https://nominatim.openstreetmap.org/search", json=mock_response)
        result = integrator.get_border_country(country)
        assert result == mock_response
        assert m.last_request.qs["country"] == [
            country.lower() if "country" in m.last_request.qs else country
        ]


def test_get_os_info(integrator, mock_token_headers):
    """Тест получения данных о самолетах"""
    borders = {"lamin": 10, "lomin": 20, "lamax": 30, "lomax": 40}
    mock_planes = {"states": [["icao24", "callsign"]]}

    with requests_mock.Mocker() as m:
        # Проверяем, что URL содержит параметры границ
        m.get(requests_mock.ANY, json=mock_planes)
        result = integrator.get_os_info(borders)

        assert result == mock_planes
        assert "lamin=10" in m.last_request.url
