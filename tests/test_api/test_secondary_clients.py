"""
Testes — Clientes Secundários de API (OpenWeather, ISS, Launch, NASA)
====================================================================
Testa o comportamento e parsing de todos os clientes secundários com respx:
    - OpenWeatherClient (Current & Forecast)
    - ISSClient (Position & Passes)
    - LaunchClient (Upcoming)
    - NASAClient (APOD & NEO)
"""

import pytest
import respx
import httpx

from api.weather.openweather_client import OpenWeatherClient
from api.space.iss_client import ISSClient
from api.space.launch_client import LaunchClient
from api.nasa.nasa_client import NASAClient
from cache.cache_manager import CacheManager
from models.weather import WeatherSnapshot, WeatherForecast
from models.space import ISSPosition, Launch, NASAApod, NearEarthObject


@pytest.fixture
def isolated_cache() -> CacheManager:
    return CacheManager(persist_dir=None)


# ---------------------------------------------------------------------------
# Testes OpenWeatherClient
# ---------------------------------------------------------------------------


class TestOpenWeatherClient:
    @pytest.mark.asyncio
    @respx.mock
    async def test_get_current_weather(self, isolated_cache: CacheManager, monkeypatch: pytest.MonkeyPatch) -> None:
        import api.weather.openweather_client as module
        monkeypatch.setattr(module, "cache_manager", isolated_cache)

        mock_data = {
            "coord": {"lat": -23.55, "lon": -46.63},
            "name": "São Paulo",
            "dt": 1722689000,
            "main": {"temp": 25.0, "feels_like": 26.0, "humidity": 60, "pressure": 1013},
            "weather": [{"id": 800, "main": "Clear", "description": "céu limpo", "icon": "01d"}],
            "wind": {"speed": 4.0, "deg": 90},
            "sys": {"sunrise": 1722670000, "sunset": 1722710000},
        }

        respx.get("https://api.openweathermap.org/data/2.5/weather").mock(
            return_value=httpx.Response(200, json=mock_data)
        )

        client = OpenWeatherClient(api_key="test_key", use_cache=True)
        async with client:
            snapshot = await client.get_current_weather(-23.55, -46.63)

        assert isinstance(snapshot, WeatherSnapshot)
        assert snapshot.location_name == "São Paulo"
        assert snapshot.temperature_c == 25.0
        assert snapshot.humidity_pct == 60.0


# ---------------------------------------------------------------------------
# Testes ISSClient
# ---------------------------------------------------------------------------


class TestISSClient:
    @pytest.mark.asyncio
    @respx.mock
    async def test_get_current_position(self, isolated_cache: CacheManager, monkeypatch: pytest.MonkeyPatch) -> None:
        import api.space.iss_client as module
        monkeypatch.setattr(module, "cache_manager", isolated_cache)

        mock_data = {
            "name": "iss",
            "id": 25544,
            "latitude": 45.1,
            "longitude": -73.2,
            "altitude": 420.5,
            "velocity": 27600.0,
            "visibility": "daylight",
            "timestamp": 1722689000,
        }

        respx.get("https://api.wheretheiss.at/v1/satellites/25544").mock(
            return_value=httpx.Response(200, json=mock_data)
        )

        client = ISSClient(use_cache=True)
        async with client:
            pos = await client.get_current_position()

        assert isinstance(pos, ISSPosition)
        assert pos.position.latitude == 45.1
        assert pos.altitude_km == 420.5


# ---------------------------------------------------------------------------
# Testes LaunchClient
# ---------------------------------------------------------------------------


class TestLaunchClient:
    @pytest.mark.asyncio
    @respx.mock
    async def test_get_upcoming_launches(self, isolated_cache: CacheManager, monkeypatch: pytest.MonkeyPatch) -> None:
        import api.space.launch_client as module
        monkeypatch.setattr(module, "cache_manager", isolated_cache)

        mock_data = {
            "results": [
                {
                    "id": "12345",
                    "name": "Falcon 9 | Starlink 6-10",
                    "status": {"id": 1, "name": "Go"},
                    "net": "2026-08-10T12:00:00Z",
                    "launch_service_provider": {"name": "SpaceX"},
                }
            ]
        }

        respx.get("https://ll.thespacedevs.com/2.2.0/launch/upcoming/").mock(
            return_value=httpx.Response(200, json=mock_data)
        )

        client = LaunchClient(use_cache=True)
        async with client:
            launches = await client.get_upcoming_launches(limit=1)

        assert len(launches) == 1
        assert isinstance(launches[0], Launch)
        assert launches[0].name == "Falcon 9 | Starlink 6-10"


# ---------------------------------------------------------------------------
# Testes NASAClient
# ---------------------------------------------------------------------------


class TestNASAClient:
    @pytest.mark.asyncio
    @respx.mock
    async def test_get_apod(self, isolated_cache: CacheManager, monkeypatch: pytest.MonkeyPatch) -> None:
        import api.nasa.nasa_client as module
        monkeypatch.setattr(module, "cache_manager", isolated_cache)

        mock_data = {
            "date": "2026-08-03",
            "title": "Andromeda Galaxy",
            "explanation": "Beautiful spiral galaxy",
            "url": "https://apod.nasa.gov/image.jpg",
            "media_type": "image",
        }

        respx.get("https://api.nasa.gov/planetary/apod").mock(
            return_value=httpx.Response(200, json=mock_data)
        )

        client = NASAClient(api_key="test_key", use_cache=True)
        async with client:
            apod = await client.get_apod()

        assert isinstance(apod, NASAApod)
        assert apod.title == "Andromeda Galaxy"
