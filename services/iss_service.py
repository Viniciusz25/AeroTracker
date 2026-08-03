"""
AeroTracker Core — ISS Service
================================
Serviço responsável pelo rastreamento da Estação Espacial Internacional (ISS).
"""

from typing import Optional

from api.space.iss_client import ISSClient
from config.settings import settings
from core.event_bus import Events
from models.space import ISSPassPrediction, ISSPosition
from services.base_service import BaseService
from utils.logger import get_logger

logger = get_logger(__name__)


class ISSService(BaseService[ISSPosition]):
    """
    Serviço da ISS.

    Args:
        client: Cliente ISSClient. Se None, cria uma instância default.
    """

    def __init__(self, client: Optional[ISSClient] = None) -> None:
        super().__init__(module_name="iss", event_name=Events.ISS_POSITION_UPDATED)
        self._client = client or ISSClient()

    async def _fetch_from_api(self) -> ISSPosition:
        """
        Busca a posição atual da ISS.

        Returns:
            ISSPosition preenchido.
        """
        async with self._client as client:
            return await client.get_current_position()

    async def get_passes(self, n_passes: int = 5) -> list[ISSPassPrediction]:
        """
        Calcula as próximas passagens da ISS sobre a localização do usuário.

        Args:
            n_passes: Número de passagens.

        Returns:
            Lista de ISSPassPrediction.
        """
        async with self._client as client:
            return await client.get_pass_predictions(
                lat=settings.default_latitude,
                lon=settings.default_longitude,
                n_passes=n_passes,
            )
