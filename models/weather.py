"""
AeroTracker Core — Modelos de Clima
======================================
Entidades de domínio para o módulo meteorológico.

Entidades:
    WeatherCondition    → Código e descrição da condição meteorológica
    WindData            → Dados de vento (velocidade, direção, rajadas)
    PrecipitationData   → Dados de precipitação (chuva, neve)
    WeatherSnapshot     → Snapshot completo de condições meteorológicas
    WeatherAlert        → Alerta meteorológico ativo
    WeatherForecast     → Previsão meteorológica (lista de snapshots)
"""

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import Field, field_validator

from models.common import AeroBaseModel, Coordinate, Velocity, VelocityUnit


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------


class WeatherConditionGroup(str, Enum):
    """Grupo de condição meteorológica (conforme padrão OpenWeather)."""
    THUNDERSTORM = "thunderstorm"
    DRIZZLE = "drizzle"
    RAIN = "rain"
    SNOW = "snow"
    ATMOSPHERE = "atmosphere"    # Névoa, neblina, fumaça, etc.
    CLEAR = "clear"
    CLOUDS = "clouds"
    UNKNOWN = "unknown"


class AlertSeverity(str, Enum):
    """Severidade de um alerta meteorológico."""
    MINOR = "minor"
    MODERATE = "moderate"
    SEVERE = "severe"
    EXTREME = "extreme"
    UNKNOWN = "unknown"


class PrecipitationType(str, Enum):
    """Tipo de precipitação."""
    RAIN = "rain"
    SNOW = "snow"
    SLEET = "sleet"
    HAIL = "hail"


# ---------------------------------------------------------------------------
# Sub-modelos
# ---------------------------------------------------------------------------


class WeatherCondition(AeroBaseModel):
    """
    Condição meteorológica atual.

    Attributes:
        code: Código numérico da condição (OpenWeather codes).
        main: Grupo principal (ex: "Rain", "Clouds").
        description: Descrição em português/inglês.
        icon: Código do ícone OpenWeather (ex: "10d").
        group: Grupo normalizado como enum.
    """

    code: int = Field(description="Código OWM da condição")
    main: str = Field(description="Grupo principal da condição")
    description: str = Field(description="Descrição detalhada")
    icon: Optional[str] = Field(default=None, description="Código do ícone")
    group: WeatherConditionGroup = Field(default=WeatherConditionGroup.UNKNOWN)

    @field_validator("main", "description", mode="before")
    @classmethod
    def strip_string(cls, v: str) -> str:
        return str(v).strip()

    @field_validator("group", mode="before")
    @classmethod
    def derive_group(cls, v: object) -> WeatherConditionGroup:
        """Permite que group seja passado como string ou deixado para derivação."""
        if isinstance(v, WeatherConditionGroup):
            return v
        if isinstance(v, str):
            try:
                return WeatherConditionGroup(v.lower())
            except ValueError:
                return WeatherConditionGroup.UNKNOWN
        return WeatherConditionGroup.UNKNOWN

    @classmethod
    def from_owm_code(cls, code: int, main: str, description: str, icon: str = "") -> "WeatherCondition":
        """Cria condição a partir dos dados brutos do OpenWeather."""
        group_map = {
            "thunderstorm": WeatherConditionGroup.THUNDERSTORM,
            "drizzle": WeatherConditionGroup.DRIZZLE,
            "rain": WeatherConditionGroup.RAIN,
            "snow": WeatherConditionGroup.SNOW,
            "atmosphere": WeatherConditionGroup.ATMOSPHERE,
            "clear": WeatherConditionGroup.CLEAR,
            "clouds": WeatherConditionGroup.CLOUDS,
        }
        group = group_map.get(main.lower(), WeatherConditionGroup.UNKNOWN)
        return cls(code=code, main=main, description=description, icon=icon, group=group)


class WindData(AeroBaseModel):
    """
    Dados de vento.

    Attributes:
        speed: Velocidade do vento.
        direction_deg: Direção de onde o vento vem (graus, 0=Norte).
        gust: Velocidade das rajadas. None se não disponível.
    """

    speed: Velocity = Field(description="Velocidade do vento")
    direction_deg: Optional[float] = Field(
        default=None,
        ge=0.0, lt=360.0,
        description="Direção do vento em graus (meteorológica)"
    )
    gust: Optional[Velocity] = Field(
        default=None,
        description="Velocidade máxima de rajadas"
    )

    @property
    def direction_name(self) -> Optional[str]:
        """Converte graus em direção cardinal (N, NE, E, etc.)."""
        if self.direction_deg is None:
            return None
        directions = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE",
                      "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"]
        idx = round(self.direction_deg / 22.5) % 16
        return directions[idx]

    @classmethod
    def from_ms(cls, speed_ms: float, direction: Optional[float] = None,
                gust_ms: Optional[float] = None) -> "WindData":
        """Cria WindData a partir de valores em m/s."""
        return cls(
            speed=Velocity(value=speed_ms, unit=VelocityUnit.METERS_PER_SECOND),
            direction_deg=direction,
            gust=Velocity(value=gust_ms, unit=VelocityUnit.METERS_PER_SECOND) if gust_ms else None,
        )


class PrecipitationData(AeroBaseModel):
    """
    Dados de precipitação.

    Attributes:
        type: Tipo de precipitação (chuva, neve, etc.).
        volume_1h: Volume na última hora (mm). None se não disponível.
        volume_3h: Volume nas últimas 3 horas (mm). None se não disponível.
    """

    type: PrecipitationType = PrecipitationType.RAIN
    volume_1h: Optional[float] = Field(
        default=None,
        ge=0.0,
        description="Volume de precipitação na última hora (mm)"
    )
    volume_3h: Optional[float] = Field(
        default=None,
        ge=0.0,
        description="Volume de precipitação nas últimas 3 horas (mm)"
    )


# ---------------------------------------------------------------------------
# Modelo principal de clima
# ---------------------------------------------------------------------------


class WeatherSnapshot(AeroBaseModel):
    """
    Snapshot completo das condições meteorológicas em um local e momento.

    Attributes:
        position: Localização da medição.
        location_name: Nome do local (cidade/estação).
        timestamp: Quando a medição foi realizada (UTC).
        temperature_c: Temperatura em Celsius.
        feels_like_c: Temperatura aparente em Celsius.
        temp_min_c: Temperatura mínima do dia.
        temp_max_c: Temperatura máxima do dia.
        humidity_pct: Umidade relativa (0-100%).
        pressure_hpa: Pressão atmosférica em hPa.
        visibility_m: Visibilidade em metros. None se não disponível.
        cloud_cover_pct: Cobertura de nuvens (0-100%). None se não disponível.
        uv_index: Índice UV. None se não disponível.
        dew_point_c: Ponto de orvalho em Celsius. None se não disponível.
        condition: Condição meteorológica atual.
        wind: Dados de vento.
        precipitation: Dados de precipitação. None se não houver.
        sunrise: Horário do nascer do sol (UTC). None se não disponível.
        sunset: Horário do pôr do sol (UTC). None se não disponível.
    """

    position: Optional[Coordinate] = None
    location_name: str = Field(description="Nome do local")
    timestamp: datetime = Field(description="Horário da medição (UTC)")

    # Temperatura
    temperature_c: float = Field(description="Temperatura em °C")
    feels_like_c: Optional[float] = Field(default=None)
    temp_min_c: Optional[float] = Field(default=None)
    temp_max_c: Optional[float] = Field(default=None)

    # Atmosfera
    humidity_pct: float = Field(ge=0.0, le=100.0, description="Umidade relativa (%)")
    pressure_hpa: float = Field(gt=0.0, description="Pressão atmosférica (hPa)")
    visibility_m: Optional[float] = Field(default=None, ge=0.0)
    cloud_cover_pct: Optional[float] = Field(default=None, ge=0.0, le=100.0)
    uv_index: Optional[float] = Field(default=None, ge=0.0)
    dew_point_c: Optional[float] = Field(default=None)

    # Condições
    condition: WeatherCondition = Field(description="Condição meteorológica")
    wind: Optional[WindData] = Field(default=None)
    precipitation: Optional[PrecipitationData] = Field(default=None)

    # Astronômico
    sunrise: Optional[datetime] = Field(default=None)
    sunset: Optional[datetime] = Field(default=None)

    @property
    def is_daytime(self) -> bool:
        """Retorna True se é horário diurno (entre nascer e pôr do sol)."""
        if self.sunrise is None or self.sunset is None:
            return True  # Assume dia se não tiver dados
        from datetime import UTC
        now = datetime.now(UTC)
        return self.sunrise <= now <= self.sunset

    @property
    def temperature_f(self) -> float:
        """Temperatura em Fahrenheit."""
        return (self.temperature_c * 9 / 5) + 32

    @classmethod
    def from_openweather(cls, data: dict) -> "WeatherSnapshot":
        """
        Cria WeatherSnapshot a partir da resposta da API OpenWeather (Current).

        Args:
            data: Dicionário JSON da resposta da OpenWeather API.

        Returns:
            WeatherSnapshot construído.
        """
        from datetime import UTC, datetime

        coord = data.get("coord", {})
        position = (
            Coordinate(latitude=coord["lat"], longitude=coord["lon"])
            if "lat" in coord and "lon" in coord
            else None
        )

        main = data.get("main", {})
        weather_list = data.get("weather", [{}])
        weather_raw = weather_list[0] if weather_list else {}

        condition = WeatherCondition.from_owm_code(
            code=weather_raw.get("id", 800),
            main=weather_raw.get("main", "Clear"),
            description=weather_raw.get("description", ""),
            icon=weather_raw.get("icon", ""),
        )

        wind_raw = data.get("wind", {})
        wind = (
            WindData.from_ms(
                speed_ms=wind_raw.get("speed", 0.0),
                direction=wind_raw.get("deg"),
                gust_ms=wind_raw.get("gust"),
            )
            if wind_raw
            else None
        )

        # Precipitação
        rain = data.get("rain", {})
        snow = data.get("snow", {})
        precipitation = None
        if rain:
            precipitation = PrecipitationData(
                type=PrecipitationType.RAIN,
                volume_1h=rain.get("1h"),
                volume_3h=rain.get("3h"),
            )
        elif snow:
            precipitation = PrecipitationData(
                type=PrecipitationType.SNOW,
                volume_1h=snow.get("1h"),
                volume_3h=snow.get("3h"),
            )

        sys_data = data.get("sys", {})
        sunrise = (
            datetime.fromtimestamp(sys_data["sunrise"], tz=UTC)
            if "sunrise" in sys_data
            else None
        )
        sunset = (
            datetime.fromtimestamp(sys_data["sunset"], tz=UTC)
            if "sunset" in sys_data
            else None
        )

        return cls(
            position=position,
            location_name=data.get("name", "Unknown"),
            timestamp=datetime.fromtimestamp(data.get("dt", 0), tz=UTC),
            temperature_c=main.get("temp", 0.0),
            feels_like_c=main.get("feels_like"),
            temp_min_c=main.get("temp_min"),
            temp_max_c=main.get("temp_max"),
            humidity_pct=main.get("humidity", 0.0),
            pressure_hpa=main.get("pressure", 1013.0),
            visibility_m=data.get("visibility"),
            cloud_cover_pct=data.get("clouds", {}).get("all"),
            condition=condition,
            wind=wind,
            precipitation=precipitation,
            sunrise=sunrise,
            sunset=sunset,
        )


class WeatherAlert(AeroBaseModel):
    """
    Alerta meteorológico ativo.

    Attributes:
        sender: Entidade que emitiu o alerta.
        event: Tipo do evento (ex: "Flood Warning", "Tempestade").
        description: Descrição detalhada do alerta.
        severity: Severidade do alerta.
        start: Início do alerta (UTC).
        end: Fim do alerta (UTC).
        tags: Tags categorizando o alerta.
    """

    sender: str = Field(description="Emissor do alerta")
    event: str = Field(description="Tipo do evento")
    description: str = Field(description="Descrição do alerta")
    severity: AlertSeverity = Field(default=AlertSeverity.UNKNOWN)
    start: Optional[datetime] = None
    end: Optional[datetime] = None
    tags: list[str] = Field(default_factory=list)

    @property
    def is_active(self) -> bool:
        """Verifica se o alerta ainda está ativo."""
        from datetime import UTC
        now = datetime.now(UTC)
        if self.start and self.start > now:
            return False
        if self.end and self.end < now:
            return False
        return True


class WeatherForecast(AeroBaseModel):
    """
    Previsão meteorológica com múltiplos snapshots.

    Attributes:
        location_name: Nome do local.
        position: Coordenada geográfica.
        snapshots: Lista de snapshots de previsão ordenados por tempo.
        alerts: Alertas meteorológicos ativos.
        timezone_offset: Offset UTC do fuso horário local (segundos).
    """

    location_name: str
    position: Optional[Coordinate] = None
    snapshots: list[WeatherSnapshot] = Field(default_factory=list)
    alerts: list[WeatherAlert] = Field(default_factory=list)
    timezone_offset: int = Field(default=0, description="Offset UTC em segundos")

    @property
    def current(self) -> Optional[WeatherSnapshot]:
        """Retorna o snapshot mais recente (primeiro da lista)."""
        return self.snapshots[0] if self.snapshots else None

    @property
    def has_alerts(self) -> bool:
        """Verifica se há alertas ativos."""
        return any(a.is_active for a in self.alerts)
