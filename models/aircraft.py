"""
AeroTracker Core — Modelos de Aeronaves
=========================================
Entidades de domínio para o módulo de rastreamento de aeronaves.

Entidades:
    AircraftCategory    → Categoria de aeronave (avião, helicóptero, etc.)
    AircraftState       → Estado atual de uma aeronave (posição, velocidade, etc.)
    Aircraft            → Aeronave completa com todos os dados
    Airport             → Aeroporto com dados IATA/ICAO
    FlightRoute         → Rota de um voo (origem → destino)
    AircraftList        → Lista de aeronaves com metadados de consulta
"""

from enum import Enum
from typing import Optional

from pydantic import Field, field_validator

from models.common import (
    AeroBaseModel,
    Altitude,
    AltitudeUnit,
    BoundingBox,
    Coordinate,
    DataSource,
    Velocity,
    VelocityUnit,
)


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------


class AircraftCategory(str, Enum):
    """
    Categoria de aeronave conforme padrão ICAO/OpenSky.

    Referência: https://opensky-network.org/apidoc/rest.html
    """
    UNKNOWN = "unknown"
    NO_INFO = "no_info"
    LIGHT = "light"                      # < 15.500 kg
    SMALL = "small"                      # 15.500 - 75.000 kg
    LARGE = "large"                      # 75.000 - 136.000 kg
    HIGH_VORTEX_LARGE = "high_vortex"    # Boeing 757
    HEAVY = "heavy"                      # > 136.000 kg
    HIGH_PERFORMANCE = "high_performance"
    ROTORCRAFT = "rotorcraft"            # Helicóptero
    GLIDER = "glider"                    # Planador
    LIGHTER_THAN_AIR = "lighter_than_air"  # Balão
    PARACHUTIST = "parachutist"
    ULTRALIGHT = "ultralight"
    RESERVED = "reserved"
    UAV = "uav"                          # Drone
    SPACE = "space"                      # Veículo espacial
    SURFACE_EMERGENCY = "surface_emergency"
    SURFACE_SERVICE = "surface_service"
    POINT_OBSTACLE = "point_obstacle"
    CLUSTER_OBSTACLE = "cluster_obstacle"
    LINE_OBSTACLE = "line_obstacle"


class AircraftStatus(str, Enum):
    """Status operacional da aeronave."""
    AIRBORNE = "airborne"          # Em voo
    ON_GROUND = "on_ground"        # Em solo
    UNKNOWN = "unknown"


class PositionSource(str, Enum):
    """Fonte do sinal de posição."""
    ADSB = "ADS-B"
    ASTERIX = "ASTERIX"
    MLAT = "MLAT"
    FLARM = "FLARM"
    UNKNOWN = "unknown"


# ---------------------------------------------------------------------------
# Modelos
# ---------------------------------------------------------------------------


class AircraftState(AeroBaseModel):
    """
    Estado atual de uma aeronave (snapshot de posição e movimento).

    Representa um único ponto no tempo dos dados de telemetria.

    Attributes:
        icao24: Código ICAO de 24 bits (transponder) — identificador único.
        callsign: Indicativo de chamada (flight number ou registration).
        origin_country: País de origem registrado.
        position: Coordenada atual (lat/lon). None se não disponível.
        altitude: Altitude barométrica. None se em solo.
        velocity: Velocidade horizontal em m/s.
        heading: Direção de proa em graus (0-360). 0=Norte.
        vertical_rate: Taxa de variação de altitude (m/s). Positivo = subindo.
        on_ground: True se a aeronave está em solo.
        squawk: Código de transponder Squawk (4 dígitos).
        last_contact: Timestamp do último contato (UNIX).
        position_source: Tipo do sensor que forneceu a posição.
        category: Categoria de aeronave ICAO.
    """

    icao24: str = Field(
        min_length=6, max_length=6,
        description="Código ICAO 24-bit (6 hex chars)"
    )
    callsign: Optional[str] = Field(
        default=None,
        description="Indicativo de chamada"
    )
    origin_country: Optional[str] = Field(
        default=None,
        description="País de origem"
    )
    position: Optional[Coordinate] = Field(
        default=None,
        description="Posição atual (lat/lon)"
    )
    altitude: Optional[Altitude] = Field(
        default=None,
        description="Altitude barométrica"
    )
    velocity: Optional[Velocity] = Field(
        default=None,
        description="Velocidade horizontal"
    )
    heading: Optional[float] = Field(
        default=None,
        ge=0.0, lt=360.0,
        description="Proa em graus (0=Norte, 90=Leste)"
    )
    vertical_rate: Optional[float] = Field(
        default=None,
        description="Taxa vertical em m/s (positivo = subindo)"
    )
    on_ground: bool = Field(
        default=False,
        description="True se em solo"
    )
    squawk: Optional[str] = Field(
        default=None,
        description="Código squawk do transponder"
    )
    last_contact: Optional[int] = Field(
        default=None,
        description="Timestamp Unix do último contato"
    )
    position_source: PositionSource = Field(
        default=PositionSource.UNKNOWN,
        description="Tipo de sensor de posição"
    )
    category: AircraftCategory = Field(
        default=AircraftCategory.UNKNOWN,
        description="Categoria ICAO da aeronave"
    )

    @field_validator("icao24", mode="before")
    @classmethod
    def normalize_icao24(cls, v: str) -> str:
        """Normaliza ICAO24 para minúsculas sem espaços."""
        return str(v).strip().lower()

    @field_validator("callsign", mode="before")
    @classmethod
    def normalize_callsign(cls, v: object) -> Optional[str]:
        """Remove espaços do callsign e retorna None se vazio."""
        if v is None:
            return None
        stripped = str(v).strip()
        return stripped if stripped else None

    @property
    def status(self) -> AircraftStatus:
        """Estado operacional derivado."""
        if self.on_ground:
            return AircraftStatus.ON_GROUND
        if self.position is not None:
            return AircraftStatus.AIRBORNE
        return AircraftStatus.UNKNOWN

    @property
    def altitude_m(self) -> Optional[float]:
        """Altitude em metros ou None."""
        if self.altitude is None:
            return None
        return self.altitude.in_meters

    @property
    def speed_kmh(self) -> Optional[float]:
        """Velocidade em km/h ou None."""
        if self.velocity is None:
            return None
        return self.velocity.in_kmh

    @property
    def display_id(self) -> str:
        """Identificador para exibição: callsign ou ICAO24."""
        return self.callsign or self.icao24.upper()

    @classmethod
    def from_opensky_state(cls, raw: list) -> "AircraftState":
        """
        Cria um AircraftState a partir de um array de estado do OpenSky.

        O OpenSky retorna estados como arrays ordenados:
        [icao24, callsign, origin_country, time_position, last_contact,
         longitude, latitude, baro_altitude, on_ground, velocity,
         true_track, vertical_rate, sensors, geo_altitude, squawk,
         spi, position_source, category]

        Args:
            raw: Array de estado do OpenSky Network.

        Returns:
            AircraftState construído a partir dos dados brutos.
        """
        def safe_float(v: object) -> Optional[float]:
            try:
                return float(v) if v is not None else None  # type: ignore[arg-type]
            except (TypeError, ValueError):
                return None

        # Posição
        lon = safe_float(raw[5]) if len(raw) > 5 else None
        lat = safe_float(raw[6]) if len(raw) > 6 else None
        position = Coordinate(latitude=lat, longitude=lon) if (
            lat is not None and lon is not None
        ) else None

        # Altitude barométrica (metros)
        baro_alt = safe_float(raw[7]) if len(raw) > 7 else None
        altitude = (
            Altitude(value=baro_alt, unit=AltitudeUnit.METERS)
            if baro_alt is not None
            else None
        )

        # Velocidade (m/s → mantemos em m/s)
        vel = safe_float(raw[9]) if len(raw) > 9 else None
        velocity = (
            Velocity(value=vel, unit=VelocityUnit.METERS_PER_SECOND)
            if vel is not None
            else None
        )

        # Categoria (índice 17 no array)
        cat_raw = raw[17] if len(raw) > 17 else 0
        category_map = {
            0: AircraftCategory.NO_INFO,
            1: AircraftCategory.NO_INFO,
            2: AircraftCategory.LIGHT,
            3: AircraftCategory.SMALL,
            4: AircraftCategory.LARGE,
            5: AircraftCategory.HIGH_VORTEX_LARGE,
            6: AircraftCategory.HEAVY,
            7: AircraftCategory.HIGH_PERFORMANCE,
            8: AircraftCategory.ROTORCRAFT,
            9: AircraftCategory.GLIDER,
            10: AircraftCategory.LIGHTER_THAN_AIR,
            11: AircraftCategory.PARACHUTIST,
            12: AircraftCategory.ULTRALIGHT,
            14: AircraftCategory.UAV,
            15: AircraftCategory.SPACE,
        }
        category = category_map.get(int(cat_raw or 0), AircraftCategory.UNKNOWN)

        # Fonte de posição
        pos_src_raw = raw[16] if len(raw) > 16 else 0
        pos_source_map = {
            0: PositionSource.ADSB,
            1: PositionSource.ASTERIX,
            2: PositionSource.MLAT,
            3: PositionSource.FLARM,
        }
        position_source = pos_source_map.get(int(pos_src_raw or 0), PositionSource.UNKNOWN)

        return cls(
            icao24=str(raw[0]) if raw[0] else "000000",
            callsign=raw[1] if len(raw) > 1 else None,
            origin_country=raw[2] if len(raw) > 2 else None,
            position=position,
            altitude=altitude,
            velocity=velocity,
            heading=safe_float(raw[10]) if len(raw) > 10 else None,
            vertical_rate=safe_float(raw[11]) if len(raw) > 11 else None,
            on_ground=bool(raw[8]) if len(raw) > 8 else False,
            squawk=str(raw[14]) if len(raw) > 14 and raw[14] else None,
            last_contact=int(raw[4]) if len(raw) > 4 and raw[4] else None,
            position_source=position_source,
            category=category,
        )


class Airport(AeroBaseModel):
    """
    Aeroporto com identificadores IATA e ICAO.

    Attributes:
        icao: Código ICAO do aeroporto (4 letras, ex: "SBGR").
        iata: Código IATA do aeroporto (3 letras, ex: "GRU"). Opcional.
        name: Nome completo do aeroporto.
        city: Cidade onde está localizado.
        country: País onde está localizado.
        position: Coordenada geográfica do aeroporto.
        altitude: Altitude do aeroporto (metros acima do nível do mar).
        timezone: Fuso horário do aeroporto.
    """

    icao: str = Field(
        min_length=4, max_length=4,
        description="Código ICAO (4 chars)"
    )
    iata: Optional[str] = Field(
        default=None,
        min_length=3, max_length=3,
        description="Código IATA (3 chars)"
    )
    name: str = Field(description="Nome do aeroporto")
    city: Optional[str] = Field(default=None)
    country: Optional[str] = Field(default=None)
    position: Optional[Coordinate] = Field(default=None)
    altitude: Optional[Altitude] = Field(default=None)
    timezone: Optional[str] = Field(default=None)

    @field_validator("icao", mode="before")
    @classmethod
    def normalize_icao(cls, v: str) -> str:
        return str(v).strip().upper()

    @field_validator("iata", mode="before")
    @classmethod
    def normalize_iata(cls, v: object) -> Optional[str]:
        if v is None:
            return None
        return str(v).strip().upper() or None


class FlightRoute(AeroBaseModel):
    """
    Rota de um voo (origem e destino).

    Attributes:
        flight_number: Número do voo (ex: "LA3501").
        airline: Nome ou código da companhia aérea.
        origin: Aeroporto de origem.
        destination: Aeroporto de destino.
        scheduled_departure: Horário programado de partida (UTC).
        scheduled_arrival: Horário programado de chegada (UTC).
    """

    flight_number: Optional[str] = Field(default=None)
    airline: Optional[str] = Field(default=None)
    origin: Optional[Airport] = Field(default=None)
    destination: Optional[Airport] = Field(default=None)
    scheduled_departure: Optional[str] = Field(default=None)
    scheduled_arrival: Optional[str] = Field(default=None)


class AircraftList(AeroBaseModel):
    """
    Lista de aeronaves retornada por uma consulta de radar.

    Attributes:
        aircraft: Lista de estados de aeronaves.
        query_time: Timestamp da consulta (UNIX).
        bounding_box: Área geográfica consultada.
        total_count: Total de aeronaves na resposta.
    """

    aircraft: list[AircraftState] = Field(default_factory=list)
    query_time: Optional[int] = Field(
        default=None,
        description="Timestamp Unix da consulta"
    )
    bounding_box: Optional[BoundingBox] = Field(default=None)

    @property
    def total_count(self) -> int:
        """Número total de aeronaves na lista."""
        return len(self.aircraft)

    @property
    def airborne_count(self) -> int:
        """Número de aeronaves em voo."""
        return sum(1 for a in self.aircraft if not a.on_ground)

    @property
    def on_ground_count(self) -> int:
        """Número de aeronaves em solo."""
        return sum(1 for a in self.aircraft if a.on_ground)

    def filter_by_country(self, country: str) -> list[AircraftState]:
        """Filtra aeronaves por país de origem."""
        return [a for a in self.aircraft if a.origin_country == country]

    def filter_by_category(self, category: AircraftCategory) -> list[AircraftState]:
        """Filtra aeronaves por categoria."""
        return [a for a in self.aircraft if a.category == category]
