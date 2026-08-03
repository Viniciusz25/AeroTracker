"""
AeroTracker Core — Bootstrap da Aplicação
==========================================
Ponto central de inicialização de todos os subsistemas.

Responsabilidades:
    - Inicializar subsistemas na ordem correta (dependências primeiro)
    - Registrar todos os módulos no ModuleManager
    - Garantir que diretórios necessários existam
    - Publicar evento de início e parada da aplicação
    - Fornecer método de shutdown gracioso

Ordem de inicialização (crítica — não alterar):
    1. Logging              (utils/logger.py)
    2. Settings             (config/settings.py)
    3. Directories          (cache_data/, storage_data/)
    4. Cache Manager        (cache/cache_manager.py)
    5. Local Storage        (storage/local_storage.py)
    6. Event Bus            (core/event_bus.py)
    7. Module Manager       (core/module_manager.py)
    8. Register Modules     (registrar todos os módulos conhecidos)

Uso:
    from core.app import AeroTrackerApp

    app = AeroTrackerApp()
    app.initialize()
    # ... lógica da aplicação ...
    app.shutdown()
"""

from typing import Any

from cache.cache_manager import cache_manager
from config.module_config import module_config
from config.settings import settings
from core.event_bus import Events, event_bus
from core.module_manager import module_manager
from storage.local_storage import local_storage
from utils.logger import get_logger, setup_logging

logger = get_logger(__name__)


# ---------------------------------------------------------------------------
# Definições de Módulos
# ---------------------------------------------------------------------------

# Catálogo de todos os módulos disponíveis no sistema.
# Cada entrada: (name, display_name, description)
_MODULE_CATALOG: list[tuple[str, str, str]] = [
    (
        "aircraft",
        "Radar de Aeronaves",
        "Rastreamento de aeronaves em tempo real via OpenSky Network e ADS-B Exchange",
    ),
    (
        "weather",
        "Clima",
        "Dados meteorológicos em tempo real via OpenWeather e Open-Meteo",
    ),
    (
        "iss",
        "Estação Espacial Internacional",
        "Rastreamento da posição da ISS em tempo real",
    ),
    (
        "launch",
        "Lançamentos Espaciais",
        "Próximos lançamentos via Launch Library 2 e SpaceX API",
    ),
    (
        "moon",
        "Lua",
        "Fase atual da Lua, horários de nascer/pôr e dados astronômicos",
    ),
    (
        "solar_system",
        "Sistema Solar",
        "Posições dos planetas e dados astronômicos do sistema solar",
    ),
    (
        "nasa",
        "NASA",
        "Imagem Astronômica do Dia (APOD) e dados de asteroides (NEO)",
    ),
    (
        "satellites",
        "Satélites",
        "Rastreamento de satélites via N2YO (requer chave de API)",
    ),
    (
        "maps",
        "Mapas",
        "Visualização cartográfica de aeronaves e objetos espaciais",
    ),
    (
        "notifications",
        "Notificações",
        "Alertas e notificações de eventos aeroespaciais",
    ),
]


# ---------------------------------------------------------------------------
# Classe Principal da Aplicação
# ---------------------------------------------------------------------------


class AeroTrackerApp:
    """
    Classe de bootstrap do AeroTracker Core.

    Responsável por inicializar todos os subsistemas na ordem correta
    e fornecer um ponto único de controle da aplicação.

    Attributes:
        _initialized: Flag que evita dupla inicialização.
    """

    def __init__(self) -> None:
        self._initialized: bool = False

    def initialize(self) -> None:
        """
        Inicializa todos os subsistemas do AeroTracker Core.

        Deve ser chamado UMA única vez no início da aplicação.
        Chamadas subsequentes são ignoradas (idempotente).

        Raises:
            RuntimeError: Se algum subsistema crítico falhar.
        """
        if self._initialized:
            logger.warning("AeroTrackerApp.initialize() chamado mais de uma vez — ignorando")
            return

        try:
            self._bootstrap()
            self._initialized = True
        except Exception as e:
            logger.critical(
                "AeroTrackerApp: falha crítica na inicialização: {err}",
                err=str(e)
            )
            raise RuntimeError(f"Falha ao inicializar AeroTracker Core: {e}") from e

    def _bootstrap(self) -> None:
        """Executa a sequência de bootstrap em ordem."""

        # --- 1. Logging ------------------------------------------------------
        setup_logging(
            log_level=settings.log_level,
            enable_file_logging=True,
        )
        logger.info("=" * 60)
        logger.info("  {name} — Iniciando", name=settings.app_name)
        logger.info("  Ambiente: {env}", env=settings.app_env)
        logger.info("=" * 60)

        # --- 2. Diretórios ---------------------------------------------------
        logger.info("[Bootstrap] Criando diretórios necessários...")
        settings.ensure_directories()
        logger.info("[Bootstrap] cache_data/ e storage_data/ prontos")

        # --- 3. Cache Manager ------------------------------------------------
        logger.info("[Bootstrap] Cache Manager: OK (singleton ativo)")

        # --- 4. Local Storage ------------------------------------------------
        logger.info("[Bootstrap] Local Storage: OK (singleton ativo)")

        # --- 5. Event Bus ----------------------------------------------------
        logger.info("[Bootstrap] Event Bus: OK (singleton ativo)")

        # --- 6. Registrar Módulos --------------------------------------------
        logger.info("[Bootstrap] Registrando módulos...")
        self._register_all_modules()

        # --- 7. Publicar evento de início ------------------------------------
        active_count = len(module_manager.get_active_modules())
        logger.info(
            "[Bootstrap] Inicialização concluída. {n} módulo(s) ativo(s).",
            n=active_count
        )

        event_bus.publish(
            Events.APP_STARTED,
            data={
                "app_name": settings.app_name,
                "environment": settings.app_env,
                "active_modules": [m.name for m in module_manager.get_active_modules()],
            },
            source="app",
        )

    def _register_all_modules(self) -> None:
        """
        Registra e ativa todos os módulos do catálogo
        conforme configuração do modules.toml.
        """
        # Mapear configuração dos módulos por nome
        module_cfg_map: dict[str, Any] = {
            "aircraft": module_config.aircraft,
            "weather": module_config.weather,
            "iss": module_config.iss,
            "launch": module_config.launch,
            "moon": module_config.moon,
            "solar_system": module_config.solar_system,
            "nasa": module_config.nasa,
            "satellites": module_config.satellites,
            "maps": module_config.maps,
            "notifications": module_config.notifications,
        }

        for name, display_name, description in _MODULE_CATALOG:
            cfg = module_cfg_map.get(name)
            enabled = cfg.enabled if cfg else False
            interval = getattr(cfg, "interval_seconds", 60) if cfg else 60

            module_manager.register(
                name=name,
                display_name=display_name,
                description=description,
                interval_seconds=interval,
                enabled_by_config=enabled,
            )

            # Ativar apenas os habilitados na configuração
            if enabled:
                module_manager.enable(name)

    # -------------------------------------------------------------------------
    # Operações em Runtime
    # -------------------------------------------------------------------------

    def shutdown(self) -> None:
        """
        Encerra a aplicação de forma graciosa.

        Publica evento de parada, limpa cache e realiza housekeeping.
        """
        logger.info("AeroTrackerApp: iniciando shutdown gracioso...")

        event_bus.publish(
            Events.APP_STOPPING,
            data={"app_name": settings.app_name},
            source="app",
        )

        # Purge de entradas expiradas no cache
        removed = cache_manager.purge_expired()
        logger.info("AeroTrackerApp: {n} entradas de cache expiradas removidas", n=removed)

        logger.info("AeroTrackerApp: shutdown concluído. Até logo! ✈")
        self._initialized = False

    def status(self) -> dict[str, Any]:
        """
        Retorna o status completo da aplicação.

        Returns:
            Dicionário com informações de todos os subsistemas.
        """
        return {
            "app": {
                "name": settings.app_name,
                "environment": settings.app_env,
                "initialized": self._initialized,
                "debug": settings.debug,
            },
            "modules": module_manager.status(),
            "cache": cache_manager.stats(),
            "event_bus": event_bus.stats(),
            "location": {
                "name": settings.default_location_name,
                "latitude": settings.default_latitude,
                "longitude": settings.default_longitude,
                "timezone": settings.default_timezone,
            },
        }

    @property
    def is_initialized(self) -> bool:
        """Retorna True se a aplicação foi inicializada com sucesso."""
        return self._initialized
