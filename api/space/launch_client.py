"""
AeroTracker Core — Launch Library 2 API Client
===============================================
Adapter para a API Launch Library 2 (The Space Devs).

Documentação: https://ll.thespacedevs.com/2.2.0/swagger/

Responsabilidades:
    - Obter os próximos lançamentos espaciais (próximas missões de SpaceX, NASA, Rocket Lab, etc.)
    - Converter respostas no modelo Launch
"""

from typing import Optional

from api.base_client import BaseAPIClient, RetryConfig
from cache.cache_manager import cache_manager
from config.settings import settings
from models.common import DataSource
from models.space import Launch
from utils.logger import get_logger

logger = get_logger(__name__)


class LaunchClient(BaseAPIClient):
    """
    Adapter para a API Launch Library 2 (LL2).

    Args:
        use_cache: Se True, ativa o CacheManager.
    """

    BASE_URL = "https://ll.thespacedevs.com/2.2.0"
    PROVIDER_NAME = "launch_library"
    _CACHE_NAMESPACE = "launch"

    def __init__(self, use_cache: bool = True) -> None:
        super().__init__(
            timeout_seconds=20.0,
            retry_config=RetryConfig(
                max_attempts=3,
                base_delay_seconds=2.0,
            ),
        )
        self._use_cache = use_cache

    async def get_upcoming_launches(self, limit: int = 10) -> list[Launch]:
        """
        Obtém a lista dos próximos lançamentos agendados.

        Args:
            limit: Número máximo de lançamentos a retornar.

        Returns:
            Lista de Launch populada.
        """
        cache_key = cache_manager.make_key("upcoming", limit)
        if self._use_cache:
            cached = cache_manager.get(self._CACHE_NAMESPACE, cache_key)
            if cached is not None:
                return cached

        params = {
            "limit": limit,
            "mode": "detailed",
        }

        raw_data = await self.get("/launch/upcoming/", params=params)

        results = raw_data.get("results", []) if isinstance(raw_data, dict) else []
        launches = []

        for item in results:
            launch = Launch.from_launchlibrary(item)
            launch.source = DataSource(provider=self.PROVIDER_NAME, cache_hit=False)
            launches.append(launch)

        if self._use_cache:
            cache_manager.set(
                self._CACHE_NAMESPACE,
                cache_key,
                launches,
                ttl=settings.cache_ttl_launch,
            )

        return launches
