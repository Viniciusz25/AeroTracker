"""
AeroTracker Core — Modelos Astronômicos
==========================================
Entidades de domínio para lua, sistema solar e eventos celestes.

Entidades:
    MoonPhase           → Fase da Lua
    MoonData            → Dados completos da Lua
    PlanetData          → Dados de um planeta do sistema solar
    SolarData           → Dados do Sol (nascer, pôr, zênite)
    AstronomicalEvent   → Evento celeste (eclipse, conjunção, etc.)
    SolarSystemSnapshot → Snapshot de todos os corpos do sistema solar
"""

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import Field, field_validator

from models.common import AeroBaseModel, Coordinate


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------


class MoonPhaseType(str, Enum):
    """Fases da Lua com nomes padronizados."""
    NEW_MOON = "new_moon"                   # Lua Nova
    WAXING_CRESCENT = "waxing_crescent"     # Lua Crescente
    FIRST_QUARTER = "first_quarter"         # Quarto Crescente
    WAXING_GIBBOUS = "waxing_gibbous"       # Gibosa Crescente
    FULL_MOON = "full_moon"                 # Lua Cheia
    WANING_GIBBOUS = "waning_gibbous"       # Gibosa Minguante
    LAST_QUARTER = "last_quarter"           # Quarto Minguante
    WANING_CRESCENT = "waning_crescent"     # Lua Minguante


class PlanetName(str, Enum):
    """Planetas do Sistema Solar."""
    MERCURY = "mercury"
    VENUS = "venus"
    EARTH = "earth"
    MARS = "mars"
    JUPITER = "jupiter"
    SATURN = "saturn"
    URANUS = "uranus"
    NEPTUNE = "neptune"
    # Não-planetas incluídos por interesse
    PLUTO = "pluto"
    SUN = "sun"
    MOON = "moon"


class EventType(str, Enum):
    """Tipo de evento astronômico."""
    SOLAR_ECLIPSE = "solar_eclipse"
    LUNAR_ECLIPSE = "lunar_eclipse"
    METEOR_SHOWER = "meteor_shower"
    PLANET_CONJUNCTION = "planet_conjunction"
    PLANET_OPPOSITION = "planet_opposition"
    SOLSTICE = "solstice"
    EQUINOX = "equinox"
    SUPERMOON = "supermoon"
    BLUE_MOON = "blue_moon"
    OTHER = "other"


# ---------------------------------------------------------------------------
# Lua
# ---------------------------------------------------------------------------


class MoonPhase(AeroBaseModel):
    """
    Fase atual da Lua.

    Attributes:
        phase_angle: Ângulo de fase (0.0 = Lua Nova, 0.5 = Lua Cheia, 1.0 = ciclo completo).
        phase_type: Tipo enumerado da fase.
        illumination_pct: Porcentagem de iluminação (0-100%).
        age_days: Idade da Lua em dias desde a última Lua Nova.
    """

    phase_angle: float = Field(
        ge=0.0, lt=1.0,
        description="Ângulo de fase normalizado (0.0 a <1.0)"
    )
    phase_type: MoonPhaseType = Field(description="Tipo da fase")
    illumination_pct: float = Field(
        ge=0.0, le=100.0,
        description="Porcentagem de iluminação"
    )
    age_days: float = Field(
        ge=0.0,
        description="Dias desde a última Lua Nova"
    )

    @classmethod
    def from_angle(cls, angle: float, illumination: float) -> "MoonPhase":
        """
        Cria MoonPhase a partir do ângulo de fase e iluminação.

        Args:
            angle: Ângulo de fase (0.0 a <1.0).
            illumination: Porcentagem de iluminação (0-100).

        Returns:
            MoonPhase com tipo derivado do ângulo.
        """
        # Derivar tipo de fase a partir do ângulo
        if angle < 0.0625 or angle >= 0.9375:
            phase_type = MoonPhaseType.NEW_MOON
        elif angle < 0.1875:
            phase_type = MoonPhaseType.WAXING_CRESCENT
        elif angle < 0.3125:
            phase_type = MoonPhaseType.FIRST_QUARTER
        elif angle < 0.4375:
            phase_type = MoonPhaseType.WAXING_GIBBOUS
        elif angle < 0.5625:
            phase_type = MoonPhaseType.FULL_MOON
        elif angle < 0.6875:
            phase_type = MoonPhaseType.WANING_GIBBOUS
        elif angle < 0.8125:
            phase_type = MoonPhaseType.LAST_QUARTER
        else:
            phase_type = MoonPhaseType.WANING_CRESCENT

        # Ciclo lunar médio: 29.53 dias
        age = angle * 29.53059

        return cls(
            phase_angle=angle,
            phase_type=phase_type,
            illumination_pct=illumination,
            age_days=age,
        )

    @property
    def phase_emoji(self) -> str:
        """Retorna emoji da fase lunar."""
        emoji_map = {
            MoonPhaseType.NEW_MOON: "🌑",
            MoonPhaseType.WAXING_CRESCENT: "🌒",
            MoonPhaseType.FIRST_QUARTER: "🌓",
            MoonPhaseType.WAXING_GIBBOUS: "🌔",
            MoonPhaseType.FULL_MOON: "🌕",
            MoonPhaseType.WANING_GIBBOUS: "🌖",
            MoonPhaseType.LAST_QUARTER: "🌗",
            MoonPhaseType.WANING_CRESCENT: "🌘",
        }
        return emoji_map.get(self.phase_type, "🌙")

    @property
    def phase_name_pt(self) -> str:
        """Retorna nome da fase em português."""
        name_map = {
            MoonPhaseType.NEW_MOON: "Lua Nova",
            MoonPhaseType.WAXING_CRESCENT: "Lua Crescente",
            MoonPhaseType.FIRST_QUARTER: "Quarto Crescente",
            MoonPhaseType.WAXING_GIBBOUS: "Gibosa Crescente",
            MoonPhaseType.FULL_MOON: "Lua Cheia",
            MoonPhaseType.WANING_GIBBOUS: "Gibosa Minguante",
            MoonPhaseType.LAST_QUARTER: "Quarto Minguante",
            MoonPhaseType.WANING_CRESCENT: "Lua Minguante",
        }
        return name_map.get(self.phase_type, "Desconhecida")


class MoonData(AeroBaseModel):
    """
    Dados completos da Lua para uma data e localização específicas.

    Attributes:
        phase: Fase atual da Lua.
        moonrise: Horário de nascer da Lua (UTC). None se não ocorrer neste dia.
        moonset: Horário de pôr da Lua (UTC). None se não ocorrer neste dia.
        next_full_moon: Data da próxima Lua Cheia.
        next_new_moon: Data da próxima Lua Nova.
        distance_km: Distância Terra-Lua em km.
        angular_diameter_deg: Diâmetro angular da Lua em graus.
        is_supermoon: True se é uma Superlua (perigeu + fase cheia).
        position: Coordenada sublunar (ponto diretamente abaixo da Lua).
        elevation_deg: Elevação da Lua no horizonte do observador.
        azimuth_deg: Azimute da Lua no horizonte do observador.
    """

    phase: MoonPhase = Field(description="Fase atual da Lua")
    moonrise: Optional[datetime] = Field(default=None)
    moonset: Optional[datetime] = Field(default=None)
    next_full_moon: Optional[datetime] = Field(default=None)
    next_new_moon: Optional[datetime] = Field(default=None)
    distance_km: Optional[float] = Field(
        default=None,
        gt=0.0,
        description="Distância Terra-Lua em km"
    )
    angular_diameter_deg: Optional[float] = Field(
        default=None,
        gt=0.0,
        description="Diâmetro angular em graus"
    )
    is_supermoon: bool = Field(default=False)
    position: Optional[Coordinate] = Field(
        default=None,
        description="Ponto sublunar (diretamente abaixo da Lua)"
    )
    elevation_deg: Optional[float] = Field(
        default=None,
        ge=-90.0, le=90.0
    )
    azimuth_deg: Optional[float] = Field(
        default=None,
        ge=0.0, lt=360.0
    )

    @property
    def is_visible(self) -> bool:
        """True se a Lua está acima do horizonte (elevação > 0)."""
        if self.elevation_deg is None:
            return False
        return self.elevation_deg > 0


# ---------------------------------------------------------------------------
# Sol
# ---------------------------------------------------------------------------


class SolarData(AeroBaseModel):
    """
    Dados solares para uma localização e data.

    Attributes:
        position: Coordenada de observação.
        date: Data da observação.
        sunrise: Horário de nascer do sol (UTC).
        sunset: Horário de pôr do sol (UTC).
        solar_noon: Horário do meio-dia solar (zênite).
        dawn: Amanhecer astronômico.
        dusk: Anoitecer astronômico.
        day_length_seconds: Duração do dia em segundos.
        elevation_deg: Elevação atual do Sol.
        azimuth_deg: Azimute atual do Sol.
        solar_declination_deg: Declinação solar.
        equation_of_time_min: Equação do tempo em minutos.
    """

    position: Optional[Coordinate] = None
    date: str = Field(description="Data de observação (YYYY-MM-DD)")

    sunrise: Optional[datetime] = None
    sunset: Optional[datetime] = None
    solar_noon: Optional[datetime] = None
    dawn: Optional[datetime] = None
    dusk: Optional[datetime] = None
    day_length_seconds: Optional[int] = Field(default=None, ge=0)

    elevation_deg: Optional[float] = Field(
        default=None, ge=-90.0, le=90.0
    )
    azimuth_deg: Optional[float] = Field(
        default=None, ge=0.0, lt=360.0
    )
    solar_declination_deg: Optional[float] = Field(
        default=None, ge=-23.5, le=23.5
    )
    equation_of_time_min: Optional[float] = None

    @property
    def day_length_formatted(self) -> str:
        """Duração do dia formatada (HH:MM:SS)."""
        if self.day_length_seconds is None:
            return "--:--:--"
        h = self.day_length_seconds // 3600
        m = (self.day_length_seconds % 3600) // 60
        s = self.day_length_seconds % 60
        return f"{h:02d}:{m:02d}:{s:02d}"

    @property
    def is_daytime(self) -> bool:
        """True se atualmente é horário diurno."""
        if self.sunrise is None or self.sunset is None:
            return False
        from datetime import UTC
        now = datetime.now(UTC)
        return self.sunrise <= now <= self.sunset


# ---------------------------------------------------------------------------
# Planetas
# ---------------------------------------------------------------------------


class PlanetData(AeroBaseModel):
    """
    Dados de um planeta do sistema solar visto de um ponto na Terra.

    Attributes:
        name: Nome do planeta.
        distance_au: Distância da Terra em Unidades Astronômicas (UA).
        magnitude: Magnitude aparente (brilho). Menor = mais brilhante.
        elevation_deg: Elevação acima do horizonte do observador.
        azimuth_deg: Azimute em relação ao horizonte do observador.
        ra_hours: Ascensão Reta em horas (0-24).
        dec_deg: Declinação em graus (-90 a +90).
        is_visible: True se está acima do horizonte e visível.
        phase_pct: Fase iluminada (0-100%). Relevante para planetas inferiores.
        angular_diameter_arcsec: Diâmetro angular em segundos de arco.
        constellation: Constelação onde o planeta está.
        rise_time: Horário de nascimento no horizonte.
        set_time: Horário de ocaso no horizonte.
    """

    name: PlanetName = Field(description="Nome do planeta")
    distance_au: Optional[float] = Field(
        default=None,
        gt=0.0,
        description="Distância em Unidades Astronômicas"
    )
    magnitude: Optional[float] = Field(
        default=None,
        description="Magnitude aparente (menor = mais brilhante)"
    )
    elevation_deg: Optional[float] = Field(
        default=None,
        ge=-90.0, le=90.0,
        description="Elevação acima do horizonte"
    )
    azimuth_deg: Optional[float] = Field(
        default=None,
        ge=0.0, lt=360.0
    )
    ra_hours: Optional[float] = Field(
        default=None,
        ge=0.0, lt=24.0,
        description="Ascensão Reta em horas"
    )
    dec_deg: Optional[float] = Field(
        default=None,
        ge=-90.0, le=90.0,
        description="Declinação em graus"
    )
    is_visible: bool = Field(default=False)
    phase_pct: Optional[float] = Field(
        default=None,
        ge=0.0, le=100.0
    )
    angular_diameter_arcsec: Optional[float] = Field(
        default=None,
        gt=0.0,
        description="Diâmetro angular em segundos de arco"
    )
    constellation: Optional[str] = None
    rise_time: Optional[datetime] = None
    set_time: Optional[datetime] = None

    @property
    def distance_km(self) -> Optional[float]:
        """Distância em km (1 UA ≈ 149.597.870 km)."""
        if self.distance_au is None:
            return None
        return self.distance_au * 149_597_870.7

    @property
    def display_name(self) -> str:
        """Nome em português para exibição."""
        pt_names = {
            "mercury": "Mercúrio",
            "venus": "Vênus",
            "earth": "Terra",
            "mars": "Marte",
            "jupiter": "Júpiter",
            "saturn": "Saturno",
            "uranus": "Urano",
            "neptune": "Netuno",
            "pluto": "Plutão",
            "sun": "Sol",
            "moon": "Lua",
        }
        # use_enum_values=True → self.name é string, não PlanetName
        key = self.name if isinstance(self.name, str) else self.name.value
        return pt_names.get(key, key.capitalize())


# ---------------------------------------------------------------------------
# Eventos Astronômicos
# ---------------------------------------------------------------------------


class AstronomicalEvent(AeroBaseModel):
    """
    Evento astronômico (eclipse, chuveiro de meteoros, etc.).

    Attributes:
        name: Nome do evento.
        event_type: Tipo categorizado.
        date: Data do evento (YYYY-MM-DD).
        datetime_utc: Data e hora exata em UTC. None se data exata desconhecida.
        description: Descrição do evento.
        visibility: Localidades onde o evento é visível.
        peak_magnitude: Magnitude de pico (para chuveiros de meteoros = meteoros/hora).
    """

    name: str = Field(description="Nome do evento")
    event_type: EventType = Field(description="Tipo do evento")
    date: str = Field(description="Data do evento (YYYY-MM-DD)")
    datetime_utc: Optional[datetime] = None
    description: Optional[str] = None
    visibility: Optional[str] = Field(
        default=None,
        description="Localidades de visibilidade"
    )
    peak_magnitude: Optional[float] = None


# ---------------------------------------------------------------------------
# Snapshot do Sistema Solar
# ---------------------------------------------------------------------------


class SolarSystemSnapshot(AeroBaseModel):
    """
    Snapshot de todos os corpos do sistema solar em um momento.

    Attributes:
        observer_position: Localização do observador.
        observed_at: Momento da observação (UTC).
        sun: Dados do Sol.
        moon: Dados da Lua.
        planets: Lista de dados dos planetas visíveis.
        upcoming_events: Próximos eventos astronômicos.
    """

    observer_position: Optional[Coordinate] = None
    observed_at: datetime = Field(description="Momento da observação")
    sun: Optional[SolarData] = None
    moon: Optional[MoonData] = None
    planets: list[PlanetData] = Field(default_factory=list)
    upcoming_events: list[AstronomicalEvent] = Field(default_factory=list)

    @property
    def visible_planets(self) -> list[PlanetData]:
        """Retorna apenas planetas visíveis acima do horizonte."""
        return [p for p in self.planets if p.is_visible]

    def get_planet(self, name: PlanetName) -> Optional[PlanetData]:
        """
        Retorna dados de um planeta específico.

        Args:
            name: Nome do planeta.

        Returns:
            PlanetData ou None se não estiver no snapshot.
        """
        return next((p for p in self.planets if p.name == name), None)
