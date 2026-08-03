"""
AeroTracker Core — ISS API Client
==================================
Adapter para rastreamento da Estação Espacial Internacional (ISS) via Open Notify & WhereTheISS.at.

Documentação:
    - https://wheretheiss.at/w4i/api
    - http://open-notify.org/Open-Notify-API/

Responsabilidades:
    - Obter a localização atual em tempo real da ISS (latitude, longitude, altitude, velocidade)
    - Calcular/obter previsões de passagem da ISS sobre uma localização específica
"""

from typing import Optional

from api.base_client import BaseAPIClient, RetryConfig
from cache.cache_manager import cache_manager
from config.settings import settings
from models.common import DataSource
from models.space import ISSPassPrediction, ISSPosition
from utils.logger import get_logger

logger = get_logger(__name__)


class ISSClient(BaseAPIClient):
    """
    Adapter para a API da ISS (WhereTheISS.at / Open-Notify).

    Args:
        use_cache: Se True, utiliza o CacheManager.
    """

    BASE_URL = "https://api.wheretheiss.at/v1"
    PROVIDER_NAME = "wheretheiss"
    _CACHE_NAMESPACE = "iss"

    def __init__(self, use_cache: bool = True) -> None:
        super().__init__(
            timeout_seconds=10.0,
            retry_config=RetryConfig(
                max_attempts=3,
                base_delay_seconds=1.0,
            ),
        )
        self._use_cache = use_cache

    async def get_current_position(self) -> ISSPosition:
        """
        Obtém a posição atual da ISS em tempo real.

        Returns:
            ISSPosition preenchido.
        """
        cache_key = "current_position"
        if self._use_cache:
            cached = cache_manager.get(self._CACHE_NAMESPACE, cache_key)
            if cached is not None:
                return cached

        # Endocentro da ISS no WhereTheISS.at é ID 25544
        raw_data = await self.get("/satellites/25544")
        position = ISSPosition.from_open_notify(raw_data)
        position.source = DataSource(provider=self.PROVIDER_NAME, cache_hit=False)

        if self._use_cache:
            cache_manager.set(
                self._CACHE_NAMESPACE,
                cache_key,
                position,
                ttl=settings.cache_ttl_iss,
            )

        return position

    async def get_pass_predictions(
        self,
        lat: float,
        lon: float,
        alt: float = 0.0,
        n_passes: int = 5,
    ) -> list[ISSPassPrediction]:
        """
        Obtém previsões de passagem da ISS sobre um ponto.

        Args:
            lat: Latitude do observador.
            lon: Longitude do observador.
            alt: Altitude em metros.
            n_passes: Número de passagens a prever.

        Returns:
            Lista de ISSPassPrediction.
        """
        cache_key = cache_manager.make_key("passes", lat, lon, alt, n_passes)
        if self._use_cache:
            cached = cache_manager.get(self._CACHE_NAMESPACE, cache_key)
            if cached is not None:
                return cached

        params = {
            "lat": lat,
            "lon": lon,
            "alt": alt,
            "n": n_passes,
        }

        raw_data = await self.get("/satellites/25544/passes", params=params)

        predictions = []
        for item in raw_data if isinstance(raw_data, list) else []:
            predictions.append(
                ISSPassPrediction(
                    rise_time=item.get("risetime", 0),
                    duration_seconds=item.get("duration", 0),
                    max_elevation_deg=item.get("max_elevation", 0.0),
                    source=DataSource(provider=self.PROVIDER_NAME, cache_hit=False),
                )
            )

        if self._use_cache:
            cache_manager.set(
                self._CACHE_NAMESPACE,
                cache_key,
                predictions,
                ttl=settings.cache_ttl_iss * 6,  # Passes mudam mais devagar
            )

        return predictions
