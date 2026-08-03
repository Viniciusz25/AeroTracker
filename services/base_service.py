"""
AeroTracker Core — Base Service
================================
Classe abstrata base para todos os serviços de negócio do AeroTracker.

Responsabilidades:
    - Encapsular lógica de atualização periódica (polling)
    - Integrar chamadas às APIs com fallback para LocalStorage em caso de erro
    - Atualizar o status do módulo via ModuleManager (record_update ou set_error)
    - Publicar eventos de dados atualizados no EventBus
    - Fornecer interface padronizada `update()` e `get_latest_data()`

Design:
    Cada serviço herda de BaseService, especifica o nome do seu módulo
    e implementa `_fetch_from_api()`.
"""

from abc import ABC, abstractmethod
from typing import Any, Generic, Optional, TypeVar

from core.event_bus import event_bus
from core.module_manager import module_manager
from storage.local_storage import local_storage
from utils.logger import get_logger

logger = get_logger(__name__)

T = TypeVar("T")


class BaseService(ABC, Generic[T]):
    """
    Classe base para os serviços de dados do AeroTracker.

    Args:
        module_name: Nome do módulo associado no ModuleManager (ex: "aircraft").
        event_name: Nome do evento a publicar no EventBus ao atualizar (ex: "aircraft.updated").
    """

    def __init__(self, module_name: str, event_name: str) -> None:
        self.module_name = module_name
        self.event_name = event_name
        self._last_data: Optional[T] = None

    @abstractmethod
    async def _fetch_from_api(self) -> T:
        """
        Método abstrato que realiza a busca de dados novos na API externa.

        Returns:
            Instância do modelo de domínio com os dados novos.
        """
        pass

    async def update(self) -> Optional[T]:
        """
        Executa o ciclo de atualização do serviço:
            1. Tenta buscar dados novos via API (`_fetch_from_api`)
            2. Se tiver sucesso:
               - Salva snapshot no LocalStorage
               - Registra sucesso no ModuleManager
               - Publica evento no EventBus
               - Atualiza `_last_data`
            3. Se falhar:
               - Marca erro no ModuleManager
               - Tenta carregar o último snapshot salvo no LocalStorage (fallback)

        Returns:
            Dados atualizados ou fallback do storage, ou None se indisponível.
        """
        if not module_manager.is_active(self.module_name):
            logger.debug("BaseService: módulo '{mod}' inativo — ignorando update", mod=self.module_name)
            return self._last_data

        logger.info("BaseService [{mod}]: iniciando atualização...", mod=self.module_name)
        try:
            data = await self._fetch_from_api()
            self._last_data = data

            # Persiste no LocalStorage
            try:
                local_storage.save(self.module_name, data, append_history=True)
            except Exception as e:
                logger.warning(
                    "BaseService [{mod}]: erro ao salvar no storage: {err}",
                    mod=self.module_name,
                    err=str(e),
                )

            # Notifica ModuleManager e EventBus
            module_manager.record_update(self.module_name)
            event_bus.publish(
                self.event_name,
                data=data,
                source=f"{self.module_name}_service",
            )

            logger.info("BaseService [{mod}]: atualização concluída com sucesso", mod=self.module_name)
            return data

        except Exception as e:
            err_msg = str(e)
            logger.error(
                "BaseService [{mod}]: falha na atualização: {err}",
                mod=self.module_name,
                err=err_msg,
            )
            module_manager.set_error(self.module_name, err_msg)

            # Fallback para LocalStorage
            fallback = self.get_latest_saved_data()
            if fallback is not None:
                logger.info(
                    "BaseService [{mod}]: utilizando dados em cache do LocalStorage como fallback",
                    mod=self.module_name,
                )
                self._last_data = fallback
                return fallback

            return self._last_data

    def get_latest_saved_data(self) -> Optional[dict]:
        """
        Recupera o último dado salvo no LocalStorage.

        Returns:
            Dicionário ou None se não houver dados salvos.
        """
        return local_storage.load_latest(self.module_name)

    @property
    def last_data(self) -> Optional[T]:
        """Retorna os dados em memória da última atualização."""
        return self._last_data
