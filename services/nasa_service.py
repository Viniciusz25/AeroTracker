"""
AeroTracker Core — NASA Service
================================
Serviço responsável por obter dados da NASA (APOD e Asteroides NEO).
"""

from datetime import datetime, UTC
from typing import Optional

from api.nasa.nasa_client import NASAClient
from core.event_bus import Events
from models.space import NASAApod, NearEarthObject
from services.base_service import BaseService
from utils.logger import get_logger

logger = get_logger(__name__)


class NASAService(BaseService[NASAApod]):
    """
    Serviço NASA.

    Args:
        client: Cliente NASAClient. Se None, cria uma instância default.
    """

    def __init__(self, client: Optional[NASAClient] = None) -> None:
        super().__init__(module_name="nasa", event_name=Events.NASA_APOD_UPDATED)
        self._client = client or NASAClient()

    async def _fetch_from_api(self) -> NASAApod:
        """
        Busca a Imagem Astronômica do Dia (APOD).

        Returns:
            NASAApod populado.
        """
        async with self._client as client:
            return await client.get_apod()

    async def get_asteroids_today(self) -> list[NearEarthObject]:
        """
        Obtém asteroides próximos da Terra marcados para o dia de hoje.

        Returns:
            Lista de NearEarthObject.
        """
        today_str = datetime.now(UTC).strftime("%Y-%m-%d")
        async with self._client as client:
            return await client.get_neo_feed(start_date=today_str, end_date=today_str)
