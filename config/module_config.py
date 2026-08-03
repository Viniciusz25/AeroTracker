"""
AeroTracker Core — Loader de Configuração de Módulos
======================================================
Carrega e valida o arquivo modules.toml, retornando
estruturas tipadas com Pydantic.

Responsabilidades:
    - Ler o arquivo config/modules.toml
    - Validar estrutura e tipos
    - Expor singleton `module_config` para uso global

Uso:
    from config.module_config import module_config

    if module_config.aircraft.enabled:
        print(module_config.aircraft.interval_seconds)
"""

import sys
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

# Suporte a TOML: Python 3.11+ tem tomllib nativo
if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib  # type: ignore[no-reorder]

_MODULES_TOML = Path(__file__).parent / "modules.toml"


# ---------------------------------------------------------------------------
# Modelos de Configuração por Módulo
# ---------------------------------------------------------------------------


class AircraftModuleConfig(BaseModel):
    """Configuração do módulo de aeronaves."""
    enabled: bool = True
    interval_seconds: int = Field(default=3, ge=1)
    provider: str = "opensky"
    max_aircraft: int = Field(default=200, ge=1, le=1000)
    radius_km: int = Field(default=250, ge=10, le=2000)


class WeatherModuleConfig(BaseModel):
    """Configuração do módulo de clima."""
    enabled: bool = True
    interval_seconds: int = Field(default=300, ge=60)
    provider: str = "openweather"


class ISSModuleConfig(BaseModel):
    """Configuração do módulo da ISS."""
    enabled: bool = True
    interval_seconds: int = Field(default=5, ge=1)


class LaunchModuleConfig(BaseModel):
    """Configuração do módulo de lançamentos espaciais."""
    enabled: bool = True
    interval_seconds: int = Field(default=600, ge=60)
    provider: str = "launchlibrary"
    upcoming_days: int = Field(default=30, ge=1, le=365)


class MoonModuleConfig(BaseModel):
    """Configuração do módulo lunar."""
    enabled: bool = True
    interval_seconds: int = Field(default=3600, ge=300)


class SolarSystemModuleConfig(BaseModel):
    """Configuração do módulo do sistema solar."""
    enabled: bool = True
    interval_seconds: int = Field(default=3600, ge=300)


class NASAModuleConfig(BaseModel):
    """Configuração do módulo NASA."""
    enabled: bool = True
    interval_seconds: int = Field(default=3600, ge=300)


class SatellitesModuleConfig(BaseModel):
    """Configuração do módulo de satélites (N2YO)."""
    enabled: bool = False
    interval_seconds: int = Field(default=30, ge=5)


class MapsModuleConfig(BaseModel):
    """Configuração do módulo de mapas."""
    enabled: bool = True
    default_zoom: int = Field(default=6, ge=1, le=20)
    tile_provider: str = "openstreetmap"


class NotificationsModuleConfig(BaseModel):
    """Configuração do módulo de notificações."""
    enabled: bool = True
    sound_enabled: bool = False
    desktop_notifications: bool = True


class ModulesConfig(BaseModel):
    """
    Configuração agregada de todos os módulos.
    Carregada a partir do arquivo config/modules.toml.
    """
    aircraft: AircraftModuleConfig = Field(default_factory=AircraftModuleConfig)
    weather: WeatherModuleConfig = Field(default_factory=WeatherModuleConfig)
    iss: ISSModuleConfig = Field(default_factory=ISSModuleConfig)
    launch: LaunchModuleConfig = Field(default_factory=LaunchModuleConfig)
    moon: MoonModuleConfig = Field(default_factory=MoonModuleConfig)
    solar_system: SolarSystemModuleConfig = Field(default_factory=SolarSystemModuleConfig)
    nasa: NASAModuleConfig = Field(default_factory=NASAModuleConfig)
    satellites: SatellitesModuleConfig = Field(default_factory=SatellitesModuleConfig)
    maps: MapsModuleConfig = Field(default_factory=MapsModuleConfig)
    notifications: NotificationsModuleConfig = Field(default_factory=NotificationsModuleConfig)

    @property
    def enabled_modules(self) -> list[str]:
        """Retorna lista de nomes dos módulos ativos."""
        return [
            name for name, cfg in self.__dict__.items()
            if hasattr(cfg, "enabled") and cfg.enabled
        ]


# ---------------------------------------------------------------------------
# Loader
# ---------------------------------------------------------------------------


def _load_module_config() -> ModulesConfig:
    """
    Carrega o arquivo modules.toml e retorna um ModulesConfig validado.

    Returns:
        ModulesConfig: Configurações tipadas de todos os módulos.

    Raises:
        FileNotFoundError: Se o arquivo modules.toml não for encontrado.
        ValueError: Se o conteúdo do TOML for inválido.
    """
    if not _MODULES_TOML.exists():
        # Fallback: retorna configuração padrão sem o arquivo
        return ModulesConfig()

    with open(_MODULES_TOML, "rb") as f:
        raw: dict[str, Any] = tomllib.load(f)

    modules_raw = raw.get("modules", {})
    return ModulesConfig(**modules_raw)


# ---------------------------------------------------------------------------
# Singleton
# ---------------------------------------------------------------------------
module_config: ModulesConfig = _load_module_config()
