"""
AeroTracker Core — Configurações Globais
==========================================
Pydantic BaseSettings carrega automaticamente variáveis de ambiente
e o arquivo .env, validando tipos e valores.

Responsabilidades:
    - Centralizar TODA configuração da aplicação
    - Validar tipos automaticamente via Pydantic
    - Expor objeto singleton `settings` para uso em qualquer módulo

Uso:
    from config.settings import settings

    print(settings.app_name)
    print(settings.openweather_api_key)
    print(settings.cache_ttl_aircraft)
"""

from pathlib import Path
from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Raiz do projeto (dois níveis acima deste arquivo)
_PROJECT_ROOT = Path(__file__).parent.parent


class AppSettings(BaseSettings):
    """
    Configurações globais do AeroTracker Core.

    Todas as propriedades são carregadas automaticamente do arquivo .env
    localizado na raiz do projeto. Valores padrão são aplicados quando
    a variável não está definida no ambiente.
    """

    model_config = SettingsConfigDict(
        env_file=_PROJECT_ROOT / ".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",          # Ignora variáveis desconhecidas no .env
    )

    # -------------------------------------------------------------------------
    # Configuração Geral
    # -------------------------------------------------------------------------
    app_name: str = Field(default="AeroTracker Core", description="Nome da aplicação")
    app_env: Literal["development", "production", "testing"] = Field(
        default="development", description="Ambiente de execução"
    )
    debug: bool = Field(default=False, description="Ativa modo debug")
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(
        default="INFO", description="Nível mínimo de logging"
    )

    # -------------------------------------------------------------------------
    # Localização
    # -------------------------------------------------------------------------
    default_latitude: float = Field(
        default=-23.5505, ge=-90.0, le=90.0,
        description="Latitude padrão do usuário"
    )
    default_longitude: float = Field(
        default=-46.6333, ge=-180.0, le=180.0,
        description="Longitude padrão do usuário"
    )
    default_timezone: str = Field(
        default="America/Sao_Paulo", description="Fuso horário padrão"
    )
    default_location_name: str = Field(
        default="São Paulo", description="Nome da localização padrão"
    )

    # -------------------------------------------------------------------------
    # APIs — Aeronaves
    # -------------------------------------------------------------------------
    opensky_username: str = Field(default="", description="Usuário OpenSky Network")
    opensky_password: str = Field(default="", description="Senha OpenSky Network")
    adsbexchange_api_key: str = Field(default="", description="Chave ADS-B Exchange")
    flightaware_api_key: str = Field(default="", description="Chave FlightAware")
    flightradar24_api_key: str = Field(default="", description="Chave FlightRadar24")

    # -------------------------------------------------------------------------
    # APIs — Clima
    # -------------------------------------------------------------------------
    openweather_api_key: str = Field(
        default="", description="Chave OpenWeatherMap"
    )
    # Open-Meteo não requer chave

    # -------------------------------------------------------------------------
    # APIs — Espaço
    # -------------------------------------------------------------------------
    nasa_api_key: str = Field(default="DEMO_KEY", description="Chave NASA API")
    # SpaceX, Launch Library 2, ISS Tracker: APIs públicas sem chave
    n2yo_api_key: str = Field(default="", description="Chave N2YO")

    # -------------------------------------------------------------------------
    # Cache
    # -------------------------------------------------------------------------
    cache_dir: Path = Field(
        default=_PROJECT_ROOT / "cache_data",
        description="Diretório para cache persistido"
    )
    cache_ttl_aircraft: int = Field(
        default=30, ge=5, description="TTL cache aeronaves (segundos)"
    )
    cache_ttl_weather: int = Field(
        default=300, ge=60, description="TTL cache clima (segundos)"
    )
    cache_ttl_iss: int = Field(
        default=5, ge=1, description="TTL cache ISS (segundos)"
    )
    cache_ttl_launch: int = Field(
        default=600, ge=60, description="TTL cache lançamentos (segundos)"
    )
    cache_ttl_moon: int = Field(
        default=3600, ge=300, description="TTL cache lua (segundos)"
    )
    cache_ttl_nasa: int = Field(
        default=3600, ge=300, description="TTL cache NASA (segundos)"
    )
    cache_ttl_satellites: int = Field(
        default=60, ge=10, description="TTL cache satélites (segundos)"
    )

    # -------------------------------------------------------------------------
    # Storage
    # -------------------------------------------------------------------------
    storage_dir: Path = Field(
        default=_PROJECT_ROOT / "storage_data",
        description="Diretório para dados históricos"
    )

    # -------------------------------------------------------------------------
    # Scheduler
    # -------------------------------------------------------------------------
    scheduler_timezone: str = Field(
        default="America/Sao_Paulo", description="Fuso horário do scheduler"
    )

    # -------------------------------------------------------------------------
    # Display
    # -------------------------------------------------------------------------
    display_theme: Literal["dark", "light"] = Field(
        default="dark", description="Tema da interface"
    )
    display_language: Literal["pt_BR", "en_US"] = Field(
        default="pt_BR", description="Idioma da interface"
    )
    window_width: int = Field(
        default=1400, ge=800, description="Largura da janela principal (px)"
    )
    window_height: int = Field(
        default=900, ge=600, description="Altura da janela principal (px)"
    )

    # -------------------------------------------------------------------------
    # Validators
    # -------------------------------------------------------------------------
    @field_validator("cache_dir", "storage_dir", mode="before")
    @classmethod
    def resolve_path(cls, v: object) -> Path:
        """Garante que caminhos relativos sejam resolvidos a partir da raiz."""
        path = Path(str(v))
        if not path.is_absolute():
            path = _PROJECT_ROOT / path
        return path

    # -------------------------------------------------------------------------
    # Propriedades derivadas
    # -------------------------------------------------------------------------
    @property
    def is_development(self) -> bool:
        """Retorna True se o ambiente for desenvolvimento."""
        return self.app_env == "development"

    @property
    def is_production(self) -> bool:
        """Retorna True se o ambiente for produção."""
        return self.app_env == "production"

    @property
    def has_opensky_credentials(self) -> bool:
        """Retorna True se credenciais OpenSky estão configuradas."""
        return bool(self.opensky_username and self.opensky_password)

    @property
    def has_openweather_key(self) -> bool:
        """Retorna True se chave OpenWeather está configurada."""
        return bool(self.openweather_api_key)

    @property
    def has_nasa_key(self) -> bool:
        """Retorna True se chave NASA está configurada (não é DEMO_KEY)."""
        return bool(self.nasa_api_key and self.nasa_api_key != "DEMO_KEY")

    def ensure_directories(self) -> None:
        """Cria os diretórios de cache e storage se não existirem."""
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.storage_dir.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------------------------
# Singleton — instância global das configurações
# ---------------------------------------------------------------------------
# Importar de qualquer módulo com: from config.settings import settings
settings = AppSettings()
