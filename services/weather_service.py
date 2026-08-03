"""
AeroTracker Core — Weather Service
===================================
Serviço responsável por gerenciar dados meteorológicos.
"""

from typing import Optional

from api.weather.openweather_client import OpenWeatherClient
from config.settings import settings
from core.event_bus import Events
from models.weather import WeatherForecast, WeatherSnapshot
from services.base_service import BaseService
from utils.logger import get_logger

logger = get_logger(__name__)


class WeatherService(BaseService[WeatherSnapshot]):
    """
    Serviço meteorológico.

    Args:
        client: Cliente OpenWeatherClient. Se None, cria uma instância default.
    """

    def __init__(self, client: Optional[OpenWeatherClient] = None) -> None:
        super().__init__(module_name="weather", event_name=Events.WEATHER_UPDATED)
        self._client = client or OpenWeatherClient()

    async def _fetch_from_api(self) -> WeatherSnapshot:
        """
        Busca o clima atual para a localização padrão.

        Returns:
            WeatherSnapshot populado.
        """
        async with self._client as client:
            return await client.get_current_weather(
                lat=settings.default_latitude,
                lon=settings.default_longitude,
            )

    async def get_forecast(self) -> WeatherForecast:
        """
        Obtém a previsão do tempo de 5 dias para a localização padrão.

        Returns:
            WeatherForecast populado.
        """
        async with self._client as client:
            return await client.get_forecast(
                lat=settings.default_latitude,
                lon=settings.default_longitude,
            )
