"""
AeroTracker Core — Gerenciador de Módulos
==========================================
Controla o ciclo de vida de todos os módulos da aplicação:
ativação, desativação e consulta de estado em runtime.

Responsabilidades:
    - Registrar módulos disponíveis no sistema
    - Ativar e desativar módulos em tempo de execução
    - Publicar eventos de ciclo de vida via EventBus
    - Fornecer status centralizado de todos os módulos
    - Respeitar configuração do modules.toml

Design:
    Cada módulo é identificado por um nome string (ex: "aircraft", "iss").
    O ModuleManager não instancia os módulos — apenas rastreia seu estado.
    A responsabilidade de instanciar é do App (bootstrap).

Uso:
    from core.module_manager import module_manager

    # Verificar se módulo está ativo
    if module_manager.is_active("aircraft"):
        ...

    # Ativar/desativar em runtime
    module_manager.enable("satellites")
    module_manager.disable("moon")

    # Status geral
    print(module_manager.status())
"""

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import Any

from core.event_bus import Events, event_bus
from utils.logger import get_logger

logger = get_logger(__name__)


# ---------------------------------------------------------------------------
# Enums e Modelos
# ---------------------------------------------------------------------------


class ModuleState(str, Enum):
    """Estados possíveis de um módulo no sistema."""
    REGISTERED = "registered"   # Registrado mas não iniciado
    ACTIVE = "active"           # Rodando normalmente
    INACTIVE = "inactive"       # Desativado pelo usuário/config
    ERROR = "error"             # Falhou ao inicializar
    STOPPING = "stopping"       # Em processo de parada


@dataclass
class ModuleInfo:
    """
    Informações de registro de um módulo.

    Attributes:
        name: Identificador único do módulo.
        display_name: Nome legível para exibição na UI.
        description: Descrição da funcionalidade.
        state: Estado atual do módulo.
        interval_seconds: Frequência de atualização configurada.
        enabled_by_config: Se está habilitado no modules.toml.
        activated_at: Timestamp de quando foi ativado.
        deactivated_at: Timestamp de quando foi desativado.
        error_message: Mensagem de erro se state == ERROR.
        update_count: Número de atualizações realizadas.
        last_updated_at: Timestamp da última atualização de dados.
    """
    name: str
    display_name: str
    description: str
    state: ModuleState = ModuleState.REGISTERED
    interval_seconds: int = 60
    enabled_by_config: bool = True
    activated_at: datetime | None = None
    deactivated_at: datetime | None = None
    error_message: str | None = None
    update_count: int = 0
    last_updated_at: datetime | None = None

    def to_dict(self) -> dict[str, Any]:
        """Serializa para dicionário (para exibição e storage)."""
        return {
            "name": self.name,
            "display_name": self.display_name,
            "description": self.description,
            "state": self.state.value,
            "interval_seconds": self.interval_seconds,
            "enabled_by_config": self.enabled_by_config,
            "activated_at": self.activated_at.isoformat() if self.activated_at else None,
            "update_count": self.update_count,
            "last_updated_at": (
                self.last_updated_at.isoformat() if self.last_updated_at else None
            ),
            "error_message": self.error_message,
        }


# ---------------------------------------------------------------------------
# Module Manager
# ---------------------------------------------------------------------------


class ModuleManager:
    """
    Gerenciador central do ciclo de vida dos módulos do AeroTracker.

    Rastreia o estado de cada módulo e publica eventos quando
    módulos são ativados, desativados ou encontram erros.
    """

    def __init__(self) -> None:
        self._modules: dict[str, ModuleInfo] = {}
        logger.info("ModuleManager inicializado")

    # -------------------------------------------------------------------------
    # Registro
    # -------------------------------------------------------------------------

    def register(
        self,
        name: str,
        display_name: str,
        description: str,
        interval_seconds: int = 60,
        enabled_by_config: bool = True,
    ) -> ModuleInfo:
        """
        Registra um módulo no gerenciador.

        Deve ser chamado durante o bootstrap da aplicação.

        Args:
            name: Identificador único (ex: "aircraft", "iss").
            display_name: Nome para exibição (ex: "Radar de Aeronaves").
            description: Descrição da funcionalidade.
            interval_seconds: Frequência de atualização em segundos.
            enabled_by_config: Se habilitado no modules.toml.

        Returns:
            ModuleInfo registrado.
        """
        if name in self._modules:
            logger.warning(
                "ModuleManager: módulo '{name}' já registrado — ignorando",
                name=name
            )
            return self._modules[name]

        state = ModuleState.INACTIVE if not enabled_by_config else ModuleState.REGISTERED

        info = ModuleInfo(
            name=name,
            display_name=display_name,
            description=description,
            interval_seconds=interval_seconds,
            enabled_by_config=enabled_by_config,
            state=state,
        )
        self._modules[name] = info

        logger.info(
            "ModuleManager: '{name}' registrado | enabled={enabled} | interval={interval}s",
            name=name, enabled=enabled_by_config, interval=interval_seconds
        )
        return info

    # -------------------------------------------------------------------------
    # Ativação / Desativação
    # -------------------------------------------------------------------------

    def enable(self, name: str) -> bool:
        """
        Ativa um módulo em runtime.

        Args:
            name: Nome do módulo a ativar.

        Returns:
            True se ativado com sucesso, False se não encontrado.
        """
        info = self._modules.get(name)
        if not info:
            logger.error(
                "ModuleManager: enable() — módulo '{name}' não registrado",
                name=name
            )
            return False

        if info.state == ModuleState.ACTIVE:
            logger.debug(
                "ModuleManager: '{name}' já está ativo",
                name=name
            )
            return True

        info.state = ModuleState.ACTIVE
        info.activated_at = datetime.now(UTC)
        info.deactivated_at = None
        info.error_message = None

        logger.info("ModuleManager: módulo '{name}' ATIVADO", name=name)
        event_bus.publish(
            Events.MODULE_ENABLED,
            data={"name": name, "display_name": info.display_name},
            source="module_manager",
        )
        return True

    def disable(self, name: str) -> bool:
        """
        Desativa um módulo em runtime.

        Args:
            name: Nome do módulo a desativar.

        Returns:
            True se desativado com sucesso, False se não encontrado.
        """
        info = self._modules.get(name)
        if not info:
            logger.error(
                "ModuleManager: disable() — módulo '{name}' não registrado",
                name=name
            )
            return False

        if info.state == ModuleState.INACTIVE:
            logger.debug("ModuleManager: '{name}' já está inativo", name=name)
            return True

        info.state = ModuleState.INACTIVE
        info.deactivated_at = datetime.now(UTC)

        logger.info("ModuleManager: módulo '{name}' DESATIVADO", name=name)
        event_bus.publish(
            Events.MODULE_DISABLED,
            data={"name": name, "display_name": info.display_name},
            source="module_manager",
        )
        return True

    def set_error(self, name: str, error_message: str) -> None:
        """
        Marca um módulo como em estado de erro.

        Args:
            name: Nome do módulo.
            error_message: Descrição do erro ocorrido.
        """
        info = self._modules.get(name)
        if not info:
            return

        info.state = ModuleState.ERROR
        info.error_message = error_message

        logger.error(
            "ModuleManager: módulo '{name}' em ERRO: {msg}",
            name=name, msg=error_message
        )
        event_bus.publish(
            Events.ERROR_API,
            data={"module": name, "error": error_message},
            source="module_manager",
        )

    def record_update(self, name: str) -> None:
        """
        Registra que um módulo completou uma atualização de dados.

        Args:
            name: Nome do módulo.
        """
        info = self._modules.get(name)
        if not info:
            return

        info.update_count += 1
        info.last_updated_at = datetime.now(UTC)

        # Se estava em erro e conseguiu atualizar, retorna ao estado ativo
        if info.state == ModuleState.ERROR:
            info.state = ModuleState.ACTIVE
            info.error_message = None
            logger.info(
                "ModuleManager: módulo '{name}' recuperado de ERRO",
                name=name
            )

    # -------------------------------------------------------------------------
    # Consultas
    # -------------------------------------------------------------------------

    def is_active(self, name: str) -> bool:
        """
        Verifica se um módulo está ativo.

        Args:
            name: Nome do módulo.

        Returns:
            True se o módulo existe e está no estado ACTIVE.
        """
        info = self._modules.get(name)
        return info is not None and info.state == ModuleState.ACTIVE

    def get(self, name: str) -> ModuleInfo | None:
        """
        Retorna informações de um módulo.

        Args:
            name: Nome do módulo.

        Returns:
            ModuleInfo ou None se não registrado.
        """
        return self._modules.get(name)

    def get_active_modules(self) -> list[ModuleInfo]:
        """Retorna lista de todos os módulos ativos."""
        return [m for m in self._modules.values() if m.state == ModuleState.ACTIVE]

    def get_all_modules(self) -> list[ModuleInfo]:
        """Retorna lista de todos os módulos registrados."""
        return list(self._modules.values())

    def status(self) -> dict[str, Any]:
        """
        Retorna um resumo do estado de todos os módulos.

        Returns:
            Dicionário com status detalhado de cada módulo.
        """
        active = [m for m in self._modules.values() if m.state == ModuleState.ACTIVE]
        inactive = [m for m in self._modules.values() if m.state == ModuleState.INACTIVE]
        errored = [m for m in self._modules.values() if m.state == ModuleState.ERROR]

        return {
            "total": len(self._modules),
            "active": len(active),
            "inactive": len(inactive),
            "error": len(errored),
            "modules": {
                name: info.to_dict()
                for name, info in self._modules.items()
            },
        }


# ---------------------------------------------------------------------------
# Singleton Global
# ---------------------------------------------------------------------------

module_manager: ModuleManager = ModuleManager()
