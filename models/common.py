"""
AeroTracker Core — Modelos Comuns
===================================
Tipos base e entidades reutilizadas em todos os módulos.

Responsabilidades:
    - Definir tipos primitivos do domínio (coordenadas, timestamps, etc.)
    - Servir de base para todos os outros modelos
    - Garantir consistência de validação entre módulos

Entidades:
    Coordinate      → Latitude/Longitude com validação de range
    Altitude        → Altitude com unidade (metros ou pés)
    Velocity        → Velocidade com unidade (m/s, km/h, knots)
    BoundingBox     → Área geográfica retangular (par de coordenadas)
    DataSource      → Origem dos dados (API, nome, timestamp)
"""

from datetime import UTC, datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, field_validator, model_validator


# ---------------------------------------------------------------------------
# Enums base
# ---------------------------------------------------------------------------


class AltitudeUnit(str, Enum):
    """Unidades de altitude."""
    METERS = "m"
    FEET = "ft"


class VelocityUnit(str, Enum):
    """Unidades de velocidade."""
    METERS_PER_SECOND = "m/s"
    KILOMETERS_PER_HOUR = "km/h"
    KNOTS = "kts"


class CardinalDirection(str, Enum):
    """Direções cardeais e subcardeais."""
    N = "N"
    NE = "NE"
    E = "E"
    SE = "SE"
    S = "S"
    SW = "SW"
    W = "W"
    NW = "NW"


# ---------------------------------------------------------------------------
# Entidades base
# ---------------------------------------------------------------------------


class Coordinate(BaseModel):
    """
    Representa uma coordenada geográfica (latitude/longitude).

    Attributes:
        latitude: Latitude em graus decimais (-90 a +90).
        longitude: Longitude em graus decimais (-180 a +180).
    """

    latitude: float = Field(
        ge=-90.0, le=90.0,
        description="Latitude em graus decimais"
    )
    longitude: float = Field(
        ge=-180.0, le=180.0,
        description="Longitude em graus decimais"
    )

    def __str__(self) -> str:
        lat_dir = "N" if self.latitude >= 0 else "S"
        lon_dir = "E" if self.longitude >= 0 else "W"
        return (
            f"{abs(self.latitude):.4f}°{lat_dir}, "
            f"{abs(self.longitude):.4f}°{lon_dir}"
        )

    def to_tuple(self) -> tuple[float, float]:
        """Retorna (latitude, longitude) como tupla."""
        return (self.latitude, self.longitude)

    def distance_km_to(self, other: "Coordinate") -> float:
        """
        Calcula a distância em km entre esta coordenada e outra
        usando a fórmula de Haversine.

        Args:
            other: Coordenada de destino.

        Returns:
            Distância em quilômetros.
        """
        import math

        r = 6371.0  # Raio médio da Terra em km
        lat1 = math.radians(self.latitude)
        lat2 = math.radians(other.latitude)
        d_lat = math.radians(other.latitude - self.latitude)
        d_lon = math.radians(other.longitude - self.longitude)

        a = (
            math.sin(d_lat / 2) ** 2
            + math.cos(lat1) * math.cos(lat2) * math.sin(d_lon / 2) ** 2
        )
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return r * c


class Altitude(BaseModel):
    """
    Altitude com unidade de medida.

    Attributes:
        value: Valor numérico da altitude.
        unit: Unidade (metros ou pés).
    """

    value: float = Field(description="Valor da altitude")
    unit: AltitudeUnit = Field(default=AltitudeUnit.METERS)

    @property
    def in_meters(self) -> float:
        """Converte para metros."""
        if self.unit == AltitudeUnit.FEET:
            return self.value * 0.3048
        return self.value

    @property
    def in_feet(self) -> float:
        """Converte para pés."""
        if self.unit == AltitudeUnit.METERS:
            return self.value / 0.3048
        return self.value

    def __str__(self) -> str:
        return f"{self.value:,.0f} {self.unit.value}"


class Velocity(BaseModel):
    """
    Velocidade com unidade de medida.

    Attributes:
        value: Valor numérico da velocidade.
        unit: Unidade (m/s, km/h ou nós).
    """

    value: float = Field(ge=0.0, description="Valor da velocidade")
    unit: VelocityUnit = Field(default=VelocityUnit.METERS_PER_SECOND)

    @property
    def in_kmh(self) -> float:
        """Converte para km/h."""
        match self.unit:
            case VelocityUnit.METERS_PER_SECOND:
                return self.value * 3.6
            case VelocityUnit.KNOTS:
                return self.value * 1.852
            case _:
                return self.value

    @property
    def in_knots(self) -> float:
        """Converte para nós."""
        match self.unit:
            case VelocityUnit.METERS_PER_SECOND:
                return self.value * 1.94384
            case VelocityUnit.KILOMETERS_PER_HOUR:
                return self.value / 1.852
            case _:
                return self.value

    def __str__(self) -> str:
        return f"{self.value:.1f} {self.unit.value}"


class BoundingBox(BaseModel):
    """
    Área geográfica retangular definida por dois cantos opostos.

    Attributes:
        min_lat: Latitude mínima (sul).
        max_lat: Latitude máxima (norte).
        min_lon: Longitude mínima (oeste).
        max_lon: Longitude máxima (leste).
    """

    min_lat: float = Field(ge=-90.0, le=90.0)
    max_lat: float = Field(ge=-90.0, le=90.0)
    min_lon: float = Field(ge=-180.0, le=180.0)
    max_lon: float = Field(ge=-180.0, le=180.0)

    @model_validator(mode="after")
    def validate_bounds(self) -> "BoundingBox":
        """Valida que min < max para lat e lon."""
        if self.min_lat >= self.max_lat:
            raise ValueError(
                f"min_lat ({self.min_lat}) deve ser menor que max_lat ({self.max_lat})"
            )
        if self.min_lon >= self.max_lon:
            raise ValueError(
                f"min_lon ({self.min_lon}) deve ser menor que max_lon ({self.max_lon})"
            )
        return self

    def contains(self, coord: Coordinate) -> bool:
        """
        Verifica se uma coordenada está dentro desta bounding box.

        Args:
            coord: Coordenada a verificar.

        Returns:
            True se a coordenada está dentro da área.
        """
        return (
            self.min_lat <= coord.latitude <= self.max_lat
            and self.min_lon <= coord.longitude <= self.max_lon
        )

    @classmethod
    def from_center_radius(
        cls,
        center: Coordinate,
        radius_km: float,
    ) -> "BoundingBox":
        """
        Cria uma BoundingBox aproximada a partir de um centro e raio em km.

        Args:
            center: Coordenada central.
            radius_km: Raio em quilômetros.

        Returns:
            BoundingBox que engloba o círculo.
        """
        import math

        # 1 grau de latitude ≈ 111.32 km
        lat_delta = radius_km / 111.32
        # Longitude varia com o cosseno da latitude
        lon_delta = radius_km / (111.32 * math.cos(math.radians(center.latitude)))

        return cls(
            min_lat=max(-90.0, center.latitude - lat_delta),
            max_lat=min(90.0, center.latitude + lat_delta),
            min_lon=max(-180.0, center.longitude - lon_delta),
            max_lon=min(180.0, center.longitude + lon_delta),
        )


class DataSource(BaseModel):
    """
    Metadados sobre a origem de um dado.

    Attributes:
        provider: Nome do provedor de dados (ex: "opensky", "nasa").
        fetched_at: Quando o dado foi obtido da API.
        cache_hit: Se os dados vieram do cache (True) ou da API (False).
        response_time_ms: Tempo de resposta da API em milissegundos.
    """

    provider: str = Field(description="Nome do provedor de dados")
    fetched_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="Timestamp de quando o dado foi obtido"
    )
    cache_hit: bool = Field(
        default=False,
        description="True se veio do cache, False se veio da API"
    )
    response_time_ms: Optional[float] = Field(
        default=None,
        ge=0.0,
        description="Tempo de resposta da API em milissegundos"
    )

    @field_validator("provider")
    @classmethod
    def provider_must_not_be_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("provider não pode ser vazio")
        return v.lower().strip()


class AeroBaseModel(BaseModel):
    """
    Classe base para todos os modelos do AeroTracker.

    Adiciona campo de origem dos dados e helpers de serialização.
    """

    source: Optional[DataSource] = Field(
        default=None,
        description="Metadados sobre a origem deste dado"
    )

    model_config = {
        "frozen": False,          # Modelos mutáveis (atualizações periódicas)
        "populate_by_name": True, # Aceita tanto alias quanto nome do campo
        "use_enum_values": True,  # Serializa enums como valores string
    }

    def to_display_dict(self) -> dict:
        """
        Serializa o modelo para um dicionário adequado para exibição na UI.
        Exclui campos internos como `source`.
        """
        return self.model_dump(
            mode="json",
            exclude={"source"},
            exclude_none=True,
        )
