"""
AeroTracker Core — Modelos Espaciais
=======================================
Entidades de domínio para os módulos ISS, Lançamentos e Satélites.

Entidades:
    ISSPosition         → Posição atual da ISS
    ISSPassPrediction   → Previsão de passagem da ISS sobre um ponto
    LaunchStatus        → Status de um lançamento
    LaunchProvider      → Provedor/agência do lançamento
    LaunchVehicle       → Veículo de lançamento (foguete)
    LaunchPad           → Plataforma de lançamento
    Launch              → Lançamento completo
    Satellite           → Satélite rastreável (N2YO)
    NASAApod            → Imagem Astronômica do Dia (NASA)
    NearEarthObject     → Asteroide próximo à Terra (NEO)
"""

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import Field, field_validator

from models.common import AeroBaseModel, Coordinate


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------


class LaunchStatusCode(str, Enum):
    """Status de um lançamento espacial (Launch Library 2)."""
    GO = "go"                    # Confirmado para lançamento
    TBD = "tbd"                  # A determinar
    SUCCESS = "success"          # Lançado com sucesso
    FAILURE = "failure"          # Falhou
    HOLD = "hold"                # Em espera
    IN_FLIGHT = "in_flight"      # Em voo
    PARTIAL_FAILURE = "partial"  # Falha parcial
    UNKNOWN = "unknown"


class OrbitType(str, Enum):
    """Tipo de órbita do lançamento."""
    LEO = "LEO"     # Low Earth Orbit
    MEO = "MEO"     # Medium Earth Orbit
    GEO = "GEO"     # Geostationary
    SSO = "SSO"     # Sun-Synchronous
    HEO = "HEO"     # High Earth Orbit
    TLI = "TLI"     # Trans-Lunar Injection
    HELIO = "HELIO" # Heliocentric
    OTHER = "other"


class SatelliteCategory(str, Enum):
    """Categoria de satélite."""
    STATION = "station"
    WEATHER = "weather"
    COMMUNICATIONS = "communications"
    NAVIGATION = "navigation"
    SCIENTIFIC = "scientific"
    MILITARY = "military"
    AMATEUR = "amateur"
    OTHER = "other"


# ---------------------------------------------------------------------------
# ISS
# ---------------------------------------------------------------------------


class ISSPosition(AeroBaseModel):
    """
    Posição atual da ISS.

    Attributes:
        position: Coordenada (lat/lon) da ISS.
        altitude_km: Altitude em quilômetros.
        velocity_kms: Velocidade em km/s.
        timestamp: Momento da medição (UNIX timestamp).
        visibility: Condição de visibilidade ("daylight", "eclipsed").
    """

    position: Coordinate = Field(description="Posição lat/lon da ISS")
    altitude_km: float = Field(
        gt=0.0,
        description="Altitude em quilômetros"
    )
    velocity_kms: float = Field(
        gt=0.0,
        description="Velocidade orbital em km/s"
    )
    timestamp: int = Field(description="Timestamp Unix da medição")
    visibility: Optional[str] = Field(
        default=None,
        description="Condição de visibilidade (daylight/eclipsed)"
    )
    footprint_km: Optional[float] = Field(
        default=None,
        description="Diâmetro da área visível em km"
    )

    @property
    def altitude_m(self) -> float:
        """Altitude em metros."""
        return self.altitude_km * 1000

    @property
    def velocity_kmh(self) -> float:
        """Velocidade em km/h."""
        return self.velocity_kms * 3600

    @property
    def is_visible_from_earth(self) -> bool:
        """Retorna True se a ISS está na parte iluminada da órbita."""
        return self.visibility == "daylight"

    @classmethod
    def from_open_notify(cls, data: dict) -> "ISSPosition":
        """
        Cria ISSPosition a partir da API Open Notify (wheretheiss.at).

        Args:
            data: Resposta JSON da API.

        Returns:
            ISSPosition construído.
        """
        return cls(
            position=Coordinate(
                latitude=float(data["latitude"]),
                longitude=float(data["longitude"]),
            ),
            altitude_km=float(data.get("altitude", 408.0)),
            velocity_kms=float(data.get("velocity", 7.66)) / 3600,  # km/h → km/s
            timestamp=int(data.get("timestamp", 0)),
            visibility=data.get("visibility"),
            footprint_km=float(data.get("footprint", 0)) or None,
        )


class ISSPassPrediction(AeroBaseModel):
    """
    Previsão de passagem da ISS sobre um ponto geográfico.

    Attributes:
        rise_time: Horário em que a ISS começa a aparecer (UTC UNIX).
        duration_seconds: Duração da passagem visível em segundos.
        max_elevation_deg: Elevação máxima durante a passagem (graus).
    """

    rise_time: int = Field(description="Timestamp de início da passagem")
    duration_seconds: int = Field(gt=0, description="Duração em segundos")
    max_elevation_deg: float = Field(
        ge=0.0, le=90.0,
        description="Elevação máxima em graus"
    )

    @property
    def rise_datetime(self) -> datetime:
        """Converte rise_time para datetime UTC."""
        from datetime import UTC
        return datetime.fromtimestamp(self.rise_time, tz=UTC)

    @property
    def duration_minutes(self) -> float:
        """Duração em minutos."""
        return self.duration_seconds / 60


# ---------------------------------------------------------------------------
# Lançamentos Espaciais
# ---------------------------------------------------------------------------


class LaunchProvider(AeroBaseModel):
    """Agência ou empresa responsável pelo lançamento."""
    id: Optional[int] = None
    name: str = Field(description="Nome da agência/empresa")
    abbrev: Optional[str] = Field(default=None, description="Abreviação")
    country_code: Optional[str] = Field(default=None)
    type: Optional[str] = Field(default=None)


class LaunchVehicle(AeroBaseModel):
    """Veículo de lançamento (foguete)."""
    id: Optional[int] = None
    name: str = Field(description="Nome do foguete")
    family: Optional[str] = Field(default=None, description="Família do foguete")
    variant: Optional[str] = Field(default=None, description="Variante")
    reusable: Optional[bool] = Field(default=None)


class LaunchPad(AeroBaseModel):
    """Plataforma de lançamento."""
    id: Optional[int] = None
    name: str = Field(description="Nome da plataforma")
    location_name: Optional[str] = Field(default=None)
    country_code: Optional[str] = Field(default=None)
    position: Optional[Coordinate] = None


class Launch(AeroBaseModel):
    """
    Lançamento espacial completo.

    Attributes:
        id: Identificador único (Launch Library 2 UUID ou SpaceX ID).
        name: Nome da missão.
        status: Status atual do lançamento.
        net: NET (No Earlier Than) — data/hora mais cedo do lançamento (UTC).
        window_start: Início da janela de lançamento.
        window_end: Fim da janela de lançamento.
        provider: Agência/empresa de lançamento.
        vehicle: Foguete utilizado.
        pad: Plataforma de lançamento.
        orbit: Tipo de órbita alvo.
        mission_description: Descrição da missão.
        image_url: URL da imagem do lançamento.
        webcast_url: URL do webcast ao vivo.
        probability: Probabilidade de lançamento (0-100%). None se desconhecido.
        hold_reason: Motivo de espera, se status == HOLD.
    """

    id: str = Field(description="ID único do lançamento")
    name: str = Field(description="Nome da missão")
    status: LaunchStatusCode = Field(
        default=LaunchStatusCode.TBD,
        description="Status atual"
    )
    net: Optional[datetime] = Field(
        default=None,
        description="No Earlier Than — data/hora mais cedo"
    )
    window_start: Optional[datetime] = Field(default=None)
    window_end: Optional[datetime] = Field(default=None)
    provider: Optional[LaunchProvider] = None
    vehicle: Optional[LaunchVehicle] = None
    pad: Optional[LaunchPad] = None
    orbit: Optional[OrbitType] = None
    mission_description: Optional[str] = None
    image_url: Optional[str] = None
    webcast_url: Optional[str] = None
    probability: Optional[float] = Field(default=None, ge=0.0, le=100.0)
    hold_reason: Optional[str] = None

    @property
    def is_upcoming(self) -> bool:
        """Retorna True se o lançamento ainda não ocorreu."""
        from datetime import UTC
        if self.net is None:
            return True
        return self.net > datetime.now(UTC)

    @property
    def is_confirmed(self) -> bool:
        """Retorna True se o lançamento está confirmado (GO)."""
        return self.status == LaunchStatusCode.GO

    @property
    def days_until_launch(self) -> Optional[float]:
        """Dias até o lançamento. None se data desconhecida."""
        if self.net is None:
            return None
        from datetime import UTC
        delta = self.net - datetime.now(UTC)
        return delta.total_seconds() / 86400

    @classmethod
    def from_launchlibrary(cls, data: dict) -> "Launch":
        """
        Cria Launch a partir da resposta da Launch Library 2 API.

        Args:
            data: Dicionário JSON de um lançamento da LL2.

        Returns:
            Launch construído.
        """
        from datetime import UTC

        def parse_dt(v: Optional[str]) -> Optional[datetime]:
            if not v:
                return None
            try:
                return datetime.fromisoformat(v.replace("Z", "+00:00"))
            except ValueError:
                return None

        status_map = {
            1: LaunchStatusCode.GO,
            2: LaunchStatusCode.TBD,
            3: LaunchStatusCode.SUCCESS,
            4: LaunchStatusCode.FAILURE,
            5: LaunchStatusCode.HOLD,
            6: LaunchStatusCode.IN_FLIGHT,
            7: LaunchStatusCode.PARTIAL_FAILURE,
        }

        status_raw = data.get("status", {})
        status_id = status_raw.get("id", 2) if isinstance(status_raw, dict) else 2
        status = status_map.get(status_id, LaunchStatusCode.TBD)

        # Provedor
        provider_raw = data.get("launch_service_provider", {}) or {}
        provider = LaunchProvider(
            id=provider_raw.get("id"),
            name=provider_raw.get("name", "Unknown"),
            abbrev=provider_raw.get("abbrev"),
            type=provider_raw.get("type", {}).get("name") if isinstance(
                provider_raw.get("type"), dict
            ) else provider_raw.get("type"),
        ) if provider_raw else None

        # Foguete
        rocket_raw = data.get("rocket", {}) or {}
        config_raw = rocket_raw.get("configuration", {}) or {}
        vehicle = LaunchVehicle(
            id=config_raw.get("id"),
            name=config_raw.get("name", "Unknown"),
            family=config_raw.get("family"),
            variant=config_raw.get("variant"),
            reusable=config_raw.get("reusable"),
        ) if config_raw else None

        # Plataforma
        pad_raw = data.get("pad", {}) or {}
        pad_location = pad_raw.get("location", {}) or {}
        pad_lat = pad_raw.get("latitude")
        pad_lon = pad_raw.get("longitude")
        pad = LaunchPad(
            id=pad_raw.get("id"),
            name=pad_raw.get("name", "Unknown"),
            location_name=pad_location.get("name"),
            country_code=pad_location.get("country_code"),
            position=(
                Coordinate(latitude=float(pad_lat), longitude=float(pad_lon))
                if pad_lat and pad_lon else None
            ),
        ) if pad_raw else None

        # Missão
        mission_raw = data.get("mission", {}) or {}
        mission_desc = mission_raw.get("description") if mission_raw else None

        # Órbita
        orbit_raw = mission_raw.get("orbit", {}) or {} if mission_raw else {}
        orbit_abbrev = orbit_raw.get("abbrev", "")
        try:
            orbit = OrbitType(orbit_abbrev) if orbit_abbrev else None
        except ValueError:
            orbit = OrbitType.OTHER if orbit_abbrev else None

        return cls(
            id=str(data.get("id", "")),
            name=data.get("name", "Unknown Mission"),
            status=status,
            net=parse_dt(data.get("net")),
            window_start=parse_dt(data.get("window_start")),
            window_end=parse_dt(data.get("window_end")),
            provider=provider,
            vehicle=vehicle,
            pad=pad,
            orbit=orbit,
            mission_description=mission_desc,
            image_url=data.get("image"),
            webcast_url=data.get("webcast_live"),
            probability=data.get("probability"),
            hold_reason=data.get("holdreason") or None,
        )


# ---------------------------------------------------------------------------
# Satélites
# ---------------------------------------------------------------------------


class Satellite(AeroBaseModel):
    """
    Satélite rastreável via N2YO ou TLE.

    Attributes:
        norad_id: Número NORAD do satélite.
        name: Nome oficial do satélite.
        category: Categoria do satélite.
        country: País de origem.
        launch_date: Data de lançamento.
        position: Posição atual (lat/lon). None se não calculado.
        altitude_km: Altitude atual em km.
        velocity_kms: Velocidade em km/s.
        elevation_deg: Elevação atual vista do ponto do observador.
        azimuth_deg: Azimute atual visto do ponto do observador.
        tle_line1: Linha 1 do TLE (Two-Line Elements).
        tle_line2: Linha 2 do TLE.
    """

    norad_id: int = Field(gt=0, description="Número NORAD do satélite")
    name: str = Field(description="Nome do satélite")
    category: SatelliteCategory = Field(default=SatelliteCategory.OTHER)
    country: Optional[str] = None
    launch_date: Optional[str] = None
    position: Optional[Coordinate] = None
    altitude_km: Optional[float] = Field(default=None, gt=0.0)
    velocity_kms: Optional[float] = Field(default=None, gt=0.0)
    elevation_deg: Optional[float] = Field(default=None, ge=-90.0, le=90.0)
    azimuth_deg: Optional[float] = Field(default=None, ge=0.0, lt=360.0)
    tle_line1: Optional[str] = None
    tle_line2: Optional[str] = None


# ---------------------------------------------------------------------------
# NASA
# ---------------------------------------------------------------------------


class NASAApod(AeroBaseModel):
    """
    Imagem Astronômica do Dia (Astronomy Picture of the Day) da NASA.

    Attributes:
        date: Data da imagem (YYYY-MM-DD).
        title: Título da imagem.
        explanation: Explicação científica.
        url: URL da imagem (pode ser vídeo).
        hdurl: URL da imagem em alta resolução. None para vídeos.
        media_type: Tipo de mídia ("image" ou "video").
        copyright: Crédito do autor. None se domínio público.
    """

    date: str = Field(description="Data (YYYY-MM-DD)")
    title: str = Field(description="Título da imagem")
    explanation: str = Field(description="Explicação científica")
    url: str = Field(description="URL da mídia")
    hdurl: Optional[str] = Field(default=None)
    media_type: str = Field(default="image")
    copyright: Optional[str] = Field(default=None)

    @property
    def is_video(self) -> bool:
        """Retorna True se a mídia é um vídeo."""
        return self.media_type == "video"

    @classmethod
    def from_nasa_api(cls, data: dict) -> "NASAApod":
        """Cria NASAApod a partir da resposta da NASA API."""
        return cls(
            date=data["date"],
            title=data["title"],
            explanation=data["explanation"],
            url=data["url"],
            hdurl=data.get("hdurl"),
            media_type=data.get("media_type", "image"),
            copyright=data.get("copyright"),
        )


class NearEarthObject(AeroBaseModel):
    """
    Objeto próximo à Terra (Near Earth Object — Asteroide/Cometa).

    Attributes:
        id: Identificador NASA.
        name: Nome do objeto.
        is_potentially_hazardous: Se é classificado como potencialmente perigoso.
        close_approach_date: Data da aproximação mais próxima.
        miss_distance_km: Distância mínima de aproximação em km.
        relative_velocity_kmh: Velocidade relativa em km/h.
        diameter_min_m: Diâmetro mínimo estimado em metros.
        diameter_max_m: Diâmetro máximo estimado em metros.
        nasa_jpl_url: URL da página JPL da NASA para mais detalhes.
    """

    id: str = Field(description="ID NASA do NEO")
    name: str = Field(description="Nome do objeto")
    is_potentially_hazardous: bool = Field(default=False)
    close_approach_date: Optional[str] = None
    miss_distance_km: Optional[float] = Field(default=None, ge=0.0)
    relative_velocity_kmh: Optional[float] = Field(default=None, ge=0.0)
    diameter_min_m: Optional[float] = Field(default=None, ge=0.0)
    diameter_max_m: Optional[float] = Field(default=None, ge=0.0)
    nasa_jpl_url: Optional[str] = None

    @property
    def diameter_avg_m(self) -> Optional[float]:
        """Diâmetro médio estimado em metros."""
        if self.diameter_min_m is None or self.diameter_max_m is None:
            return None
        return (self.diameter_min_m + self.diameter_max_m) / 2
