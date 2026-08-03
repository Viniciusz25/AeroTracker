"""
AeroTracker Core — OpenSky Network API Client
===============================================
Adapter para a API REST do OpenSky Network.

Documentação: https://opensky-network.org/apidoc/rest.html

Responsabilidades:
    - Buscar aeronaves em tempo real dentro de uma área geográfica
    - Converter resposta bruta da API em objetos AircraftList tipados
    - Suportar autenticação anônima e autenticada
    - Respeitar limites de rate da API:
        * Anônimo: 400 req/dia, dados com 10s de atraso
        * Autenticado: 4000 req/dia, dados em tempo real

Endpoints utilizados:
    GET /states/all
        Retorna o estado de todas as aeronaves em uma bounding box.
        Parâmetros: lamin, lamax, lomin, lomax, time (opcional)

Uso:
    from api.aircraft.opensky_client import OpenSkyClient

    async with OpenSkyClient() as client:
        aircraft_list = await client.get_aircraft_in_area(
            lat=-23.5505, lon=-46.6333, radius_km=250
        )
        print(f'{aircraft_list.total_count} aeronaves detectadas')
"""

from typing import Optional

from api.base_client import BaseAPIClient, RetryConfig
from cache.cache_manager import cache_manager
from config.settings import settings
from models.aircraft import AircraftList, AircraftState
from models.common import BoundingBox, Coordinate, DataSource
from utils.logger import get_logger

logger = get_logger(__name__)


class OpenSkyClient(BaseAPIClient):
    """
    Adapter para a API OpenSky Network.

    Suporta acesso anônimo (sem chave) e autenticado.
    O acesso autenticado oferece dados mais frescos e maior limite de requisições.

    O cliente integra automaticamente com o CacheManager para evitar
    chamadas desnecessárias dentro do TTL configurado.

    Args:
        username: Usuário OpenSky. None para acesso anônimo.
        password: Senha OpenSky. None para acesso anônimo.
        use_cache: Se True, usa cache automático com TTL das settings.
    """

    BASE_URL = "https://opensky-network.org/api"
    PROVIDER_NAME = "opensky"

    _ENDPOINT_STATES = "/states/all"
    _CACHE_NAMESPACE = "aircraft"

    def __init__(
        self,
        username: Optional[str] = None,
        password: Optional[str] = None,
        use_cache: bool = True,
    ) -> None:
        # Credenciais da configuração se não passadas explicitamente
        _username = username or settings.opensky_username or None
        _password = password or settings.opensky_password or None

        auth = (_username, _password) if (_username and _password) else None

        super().__init__(
            timeout_seconds=20.0,
            retry_config=RetryConfig(
                max_attempts=3,
                base_delay_seconds=2.0,
                max_delay_seconds=15.0,
            ),
            auth=auth,
        )

        self._use_cache = use_cache
        self._is_authenticated = auth is not None

        logger.info(
            "OpenSkyClient: modo={mode}",
            mode="autenticado" if self._is_authenticated else "anônimo",
        )

    # -------------------------------------------------------------------------
    # API Pública
    # -------------------------------------------------------------------------

    async def get_aircraft_in_area(
        self,
        lat: float,
        lon: float,
        radius_km: float = 250.0,
        time_secs: Optional[int] = None,
    ) -> AircraftList:
        """
        Retorna aeronaves detectadas dentro de um raio a partir de um ponto.

        Internamente converte o raio em bounding box retangular para
        compatibilidade com a API do OpenSky.

        Args:
            lat: Latitude do centro da busca.
            lon: Longitude do centro da busca.
            radius_km: Raio de busca em quilômetros.
            time_secs: Timestamp Unix para consulta histórica.
                       None = dados mais recentes.

        Returns:
            AircraftList com todas as aeronaves na área.

        Raises:
            APIError: Se a requisição falhar após todas as tentativas de retry.
        """
        center = Coordinate(latitude=lat, longitude=lon)
        bbox = BoundingBox.from_center_radius(center, radius_km=radius_km)

        return await self.get_aircraft_in_bbox(bbox, time_secs=time_secs)

    async def get_aircraft_in_bbox(
        self,
        bbox: BoundingBox,
        time_secs: Optional[int] = None,
    ) -> AircraftList:
        """
        Retorna aeronaves dentro de uma bounding box geográfica.

        Args:
            bbox: Área geográfica de busca.
            time_secs: Timestamp Unix para consulta histórica.

        Returns:
            AircraftList com todas as aeronaves na área.

        Raises:
            APIError: Se a requisição falhar.
        """
        # Verificar cache
        cache_key = cache_manager.make_key(
            bbox.min_lat, bbox.max_lat, bbox.min_lon, bbox.max_lon,
            time_secs or "live"
        )

        if self._use_cache:
            cached = cache_manager.get(self._CACHE_NAMESPACE, cache_key)
            if cached is not None:
                logger.debug("OpenSky: cache HIT para bbox={bbox}", bbox=cache_key)
                return cached

        # Fazer requisição
        logger.info(
            "OpenSky: buscando aeronaves | bbox=[{lat1},{lat2},{lon1},{lon2}]",
            lat1=round(bbox.min_lat, 2),
            lat2=round(bbox.max_lat, 2),
            lon1=round(bbox.min_lon, 2),
            lon2=round(bbox.max_lon, 2),
        )

        params: dict = {
            "lamin": bbox.min_lat,
            "lamax": bbox.max_lat,
            "lomin": bbox.min_lon,
            "lomax": bbox.max_lon,
        }
        if time_secs is not None:
            params["time"] = time_secs

        raw_data = await self.get(self._ENDPOINT_STATES, params=params)
        aircraft_list = self._parse_response(raw_data, bbox)

        # Salvar no cache
        if self._use_cache:
            cache_manager.set(
                self._CACHE_NAMESPACE,
                cache_key,
                aircraft_list,
                ttl=settings.cache_ttl_aircraft,
            )

        logger.info(
            "OpenSky: {n} aeronaves ({airborne} em voo) | query_time={qt}",
            n=aircraft_list.total_count,
            airborne=aircraft_list.airborne_count,
            qt=aircraft_list.query_time,
        )

        return aircraft_list

    async def get_aircraft_by_icao24(self, icao24: str) -> Optional[AircraftState]:
        """
        Busca o estado atual de uma aeronave específica pelo ICAO24.

        Args:
            icao24: Código ICAO 24-bit (6 caracteres hex).

        Returns:
            AircraftState ou None se não encontrada.
        """
        icao24 = icao24.lower().strip()
        cache_key = f"icao24_{icao24}"

        if self._use_cache:
            cached = cache_manager.get(self._CACHE_NAMESPACE, cache_key)
            if cached is not None:
                return cached

        params = {"icao24": icao24}
        raw_data = await self.get(self._ENDPOINT_STATES, params=params)
        aircraft_list = self._parse_response(raw_data, bbox=None)

        result = aircraft_list.aircraft[0] if aircraft_list.aircraft else None

        if self._use_cache and result:
            cache_manager.set(
                self._CACHE_NAMESPACE,
                cache_key,
                result,
                ttl=settings.cache_ttl_aircraft,
            )

        return result

    # -------------------------------------------------------------------------
    # Parsing
    # -------------------------------------------------------------------------

    def _parse_response(
        self,
        raw_data: dict,
        bbox: Optional[BoundingBox],
    ) -> AircraftList:
        """
        Converte a resposta bruta da API em um AircraftList tipado.

        O OpenSky retorna:
        {
            "time": <unix_timestamp>,
            "states": [
                [icao24, callsign, origin_country, time_position, last_contact,
                 longitude, latitude, baro_altitude, on_ground, velocity,
                 true_track, vertical_rate, sensors, geo_altitude, squawk,
                 spi, position_source, category],
                ...
            ]
        }

        Args:
            raw_data: Resposta JSON da API.
            bbox: Bounding box da consulta (para metadados).

        Returns:
            AircraftList com objetos AircraftState tipados.
        """
        if not raw_data or not isinstance(raw_data, dict):
            logger.warning("OpenSky: resposta vazia ou inválida")
            return AircraftList(
                aircraft=[],
                query_time=None,
                bounding_box=bbox,
                source=DataSource(provider=self.PROVIDER_NAME),
            )

        states_raw = raw_data.get("states") or []
        query_time = raw_data.get("time")

        aircraft_list = []
        parse_errors = 0

        for state_array in states_raw:
            if not state_array or len(state_array) < 8:
                continue
            try:
                aircraft = AircraftState.from_opensky_state(state_array)
                aircraft_list.append(aircraft)
            except Exception as e:
                parse_errors += 1
                logger.debug(
                    "OpenSky: erro ao parsear estado {icao}: {err}",
                    icao=state_array[0] if state_array else "?",
                    err=str(e),
                )

        if parse_errors:
            logger.warning(
                "OpenSky: {n} aeronaves não puderam ser parseadas",
                n=parse_errors,
            )

        return AircraftList(
            aircraft=aircraft_list,
            query_time=query_time,
            bounding_box=bbox,
            source=DataSource(
                provider=self.PROVIDER_NAME,
                cache_hit=False,
            ),
        )
