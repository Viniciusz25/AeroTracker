"""
AeroTracker Core — NASA API Client
===================================
Adapter para as APIs oficiais da NASA (APOD e NEO / NeoWs).

Documentação: https://api.nasa.gov/

Responsabilidades:
    - Obter a Imagem Astronômica do Dia (APOD)
    - Obter objetos próximos à Terra / Asteroides (NEO)
"""

from datetime import datetime
from typing import Optional

from api.base_client import BaseAPIClient, RetryConfig
from cache.cache_manager import cache_manager
from config.settings import settings
from models.common import DataSource
from models.space import NASAApod, NearEarthObject
from utils.logger import get_logger

logger = get_logger(__name__)


class NASAClient(BaseAPIClient):
    """
    Adapter para as APIs da NASA.

    Args:
        api_key: Chave API da NASA. Se None, usa settings.nasa_api_key.
        use_cache: Se True, usa o CacheManager.
    """

    BASE_URL = "https://api.nasa.gov"
    PROVIDER_NAME = "nasa"
    _CACHE_NAMESPACE = "nasa"

    def __init__(
        self,
        api_key: Optional[str] = None,
        use_cache: bool = True,
    ) -> None:
        self._api_key = api_key or settings.nasa_api_key
        super().__init__(
            timeout_seconds=15.0,
            retry_config=RetryConfig(
                max_attempts=3,
                base_delay_seconds=1.0,
            ),
        )
        self._use_cache = use_cache

    async def get_apod(self, date: Optional[str] = None) -> NASAApod:
        """
        Obtém a Imagem Astronômica do Dia (APOD).

        Args:
            date: Data no formato YYYY-MM-DD. None = foto de hoje.

        Returns:
            NASAApod populado.
        """
        cache_key = cache_manager.make_key("apod", date or "today")
        if self._use_cache:
            cached = cache_manager.get(self._CACHE_NAMESPACE, cache_key)
            if cached is not None:
                return cached

        params = {"api_key": self._api_key}
        if date:
            params["date"] = date

        raw_data = await self.get("/planetary/apod", params=params)
        apod = NASAApod.from_nasa_api(raw_data)
        apod.source = DataSource(provider=self.PROVIDER_NAME, cache_hit=False)

        if self._use_cache:
            cache_manager.set(
                self._CACHE_NAMESPACE,
                cache_key,
                apod,
                ttl=settings.cache_ttl_nasa,
            )

        return apod

    async def get_neo_feed(
        self,
        start_date: str,
        end_date: Optional[str] = None,
    ) -> list[NearEarthObject]:
        """
        Obtém asteroides/objetos próximos à Terra em um intervalo de datas.

        Args:
            start_date: Data inicial (YYYY-MM-DD).
            end_date: Data final (YYYY-MM-DD).

        Returns:
            Lista de NearEarthObject.
        """
        cache_key = cache_manager.make_key("neo", start_date, end_date or "same")
        if self._use_cache:
            cached = cache_manager.get(self._CACHE_NAMESPACE, cache_key)
            if cached is not None:
                return cached

        params = {
            "start_date": start_date,
            "api_key": self._api_key,
        }
        if end_date:
            params["end_date"] = end_date

        raw_data = await self.get("/neo/rest/v1/feed", params=params)

        neo_list = []
        near_earth_objects = raw_data.get("near_earth_objects", {})

        for date_str, items in near_earth_objects.items():
            for item in items:
                estimated_diam = item.get("estimated_diameter", {}).get("meters", {})
                close_approach = (
                    item.get("close_approach_data", [{}])[0]
                    if item.get("close_approach_data")
                    else {}
                )

                miss_dist = close_approach.get("miss_distance", {}).get("kilometers")
                rel_vel = close_approach.get("relative_velocity", {}).get(
                    "kilometers_per_hour"
                )

                neo = NearEarthObject(
                    id=str(item.get("id")),
                    name=item.get("name", "Unknown"),
                    is_potentially_hazardous=bool(
                        item.get("is_potentially_hazardous_asteroid", False)
                    ),
                    close_approach_date=close_approach.get("close_approach_date"),
                    miss_distance_km=float(miss_dist) if miss_dist else None,
                    relative_velocity_kmh=float(rel_vel) if rel_vel else None,
                    diameter_min_m=float(estimated_diam.get("estimated_diameter_min", 0)),
                    diameter_max_m=float(estimated_diam.get("estimated_diameter_max", 0)),
                    nasa_jpl_url=item.get("nasa_jpl_url"),
                    source=DataSource(provider=self.PROVIDER_NAME, cache_hit=False),
                )
                neo_list.append(neo)

        if self._use_cache:
            cache_manager.set(
                self._CACHE_NAMESPACE,
                cache_key,
                neo_list,
                ttl=settings.cache_ttl_nasa,
            )

        return neo_list
