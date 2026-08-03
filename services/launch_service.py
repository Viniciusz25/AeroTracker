"""
AeroTracker Core — Launch Service
==================================
Serviço responsável por acompanhar lançamentos espaciais.
"""

from typing import Optional

from api.space.launch_client import LaunchClient
from core.event_bus import Events
from models.space import Launch
from services.base_service import BaseService
from utils.logger import get_logger

logger = get_logger(__name__)


class LaunchService(BaseService[list[Launch]]):
    """
    Serviço de lançamentos espaciais.

    Args:
        client: Cliente LaunchClient. Se None, cria uma instância default.
    """

    def __init__(self, client: Optional[LaunchClient] = None) -> None:
        super().__init__(module_name="launch", event_name=Events.LAUNCH_UPDATED)
        self._client = client or LaunchClient()

    async def _fetch_from_api(self) -> list[Launch]:
        """
        Busca os próximos 10 lançamentos agendados no mundo.

        Returns:
            Lista de Launch.
        """
        async with self._client as client:
            return await client.get_upcoming_launches(limit=10)
