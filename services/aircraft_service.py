"""
AeroTracker Core — Aircraft Service
====================================
Serviço responsável por gerenciar dados do radar de aeronaves.
"""

from typing import Optional

from api.aircraft.opensky_client import OpenSkyClient
from config.settings import settings
from core.event_bus import Events
from models.aircraft import AircraftList, AircraftState
from services.base_service import BaseService
from utils.logger import get_logger

logger = get_logger(__name__)


class AircraftService(BaseService[AircraftList]):
    """
    Serviço de radar de aeronaves.

    Args:
        client: Cliente OpenSkyClient. Se None, cria uma instância default.
    """

    def __init__(self, client: Optional[OpenSkyClient] = None) -> None:
        super().__init__(module_name="aircraft", event_name=Events.AIRCRAFT_UPDATED)
        self._client = client or OpenSkyClient()

    async def _fetch_from_api(self) -> AircraftList:
        """
        Busca aeronaves na região padrão configurada.

        Returns:
            AircraftList com as aeronaves na área.
        """
        async with self._client as client:
            return await client.get_aircraft_in_area(
                lat=settings.default_latitude,
                lon=settings.default_longitude,
                radius_km=250.0,
            )

    async def get_aircraft_by_icao(self, icao24: str) -> Optional[AircraftState]:
        """
        Busca aeronave específica pelo código ICAO24.

        Args:
            icao24: Código ICAO 24-bit.

        Returns:
            AircraftState ou None.
        """
        async with self._client as client:
            return await client.get_aircraft_by_icao24(icao24)
