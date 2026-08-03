"""
AeroTracker Core — OpenWeather API Client
=========================================
Adapter para as APIs OpenWeather (Current Weather Data & One Call / Forecast).

Documentação: https://openweathermap.org/current

Responsabilidades:
    - Obter dados meteorológicos atuais por coordenadas ou nome de cidade
    - Obter previsões e alertas meteorológicos
    - Converter respostas em modelos WeatherSnapshot e WeatherForecast
    - Integrar com CacheManager e utilizar a chave OpenWeather configurada
"""

from typing import Any, Optional

from api.base_client import BaseAPIClient, RetryConfig
from cache.cache_manager import cache_manager
from config.settings import settings
from models.common import Coordinate, DataSource
from models.weather import WeatherForecast, WeatherSnapshot
from utils.logger import get_logger

logger = get_logger(__name__)


class OpenWeatherClient(BaseAPIClient):
    """
    Adapter para a API OpenWeather.

    Args:
        api_key: Chave de API do OpenWeather. Se None, usa settings.openweather_api_key.
        use_cache: Se True, ativa o cache automático.
    """

    BASE_URL = "https://api.openweathermap.org/data/2.5"
    PROVIDER_NAME = "openweather"
    _CACHE_NAMESPACE = "weather"

    def __init__(
        self,
        api_key: Optional[str] = None,
        use_cache: bool = True,
    ) -> None:
        self._api_key = api_key or settings.openweather_api_key
        if not self._api_key:
            logger.warning("OpenWeatherClient: nenhuma API key configurada")

        super().__init__(
            timeout_seconds=15.0,
            retry_config=RetryConfig(
                max_attempts=3,
                base_delay_seconds=1.0,
            ),
        )
        self._use_cache = use_cache

    async def get_current_weather(
        self,
        lat: float,
        lon: float,
        units: str = "metric",
        lang: str = "pt_br",
    ) -> WeatherSnapshot:
        """
        Obtém o clima atual para uma coordenada geográfica.

        Args:
            lat: Latitude.
            lon: Longitude.
            units: Unidades de medida ("metric", "imperial", "standard").
            lang: Idioma das descrições.

        Returns:
            WeatherSnapshot populado com os dados da API.
        """
        cache_key = cache_manager.make_key("current", lat, lon, units, lang)
        if self._use_cache:
            cached = cache_manager.get(self._CACHE_NAMESPACE, cache_key)
            if cached is not None:
                logger.debug("OpenWeather: cache HIT para ({lat}, {lon})", lat=lat, lon=lon)
                return cached

        params = {
            "lat": lat,
            "lon": lon,
            "appid": self._api_key,
            "units": units,
            "lang": lang,
        }

        raw_data = await self.get("/weather", params=params)
        snapshot = WeatherSnapshot.from_openweather(raw_data)
        snapshot.source = DataSource(provider=self.PROVIDER_NAME, cache_hit=False)

        if self._use_cache:
            cache_manager.set(
                self._CACHE_NAMESPACE,
                cache_key,
                snapshot,
                ttl=settings.cache_ttl_weather,
            )

        return snapshot

    async def get_forecast(
        self,
        lat: float,
        lon: float,
        units: str = "metric",
        lang: str = "pt_br",
    ) -> WeatherForecast:
        """
        Obtém a previsão de 5 dias / 3 horas para uma coordenada.

        Args:
            lat: Latitude.
            lon: Longitude.
            units: Unidades.
            lang: Idioma.

        Returns:
            WeatherForecast com lista de snapshots.
        """
        cache_key = cache_manager.make_key("forecast", lat, lon, units, lang)
        if self._use_cache:
            cached = cache_manager.get(self._CACHE_NAMESPACE, cache_key)
            if cached is not None:
                return cached

        params = {
            "lat": lat,
            "lon": lon,
            "appid": self._api_key,
            "units": units,
            "lang": lang,
        }

        raw_data = await self.get("/forecast", params=params)

        city_name = raw_data.get("city", {}).get("name", "Unknown")
        snapshots = []
        for item in raw_data.get("list", []):
            item["name"] = city_name
            item["coord"] = {"lat": lat, "lon": lon}
            snapshots.append(WeatherSnapshot.from_openweather(item))

        forecast = WeatherForecast(
            location_name=city_name,
            position=Coordinate(latitude=lat, longitude=lon),
            snapshots=snapshots,
            source=DataSource(provider=self.PROVIDER_NAME, cache_hit=False),
        )

        if self._use_cache:
            cache_manager.set(
                self._CACHE_NAMESPACE,
                cache_key,
                forecast,
                ttl=settings.cache_ttl_weather,
            )

        return forecast
