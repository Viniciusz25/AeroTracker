"""
AeroTracker Core — Agendador de Tarefas (Background Scheduler)
================================================================
Engine de agendamento assíncrono para polling de dados dos módulos.

Responsabilidades:
    - Inicializar e gerenciar o agendador assíncrono de background (APScheduler)
    - Registrar jobs periódicos para os módulos cadastrados no ModuleManager
    - Ajustar intervalos dinamicamente conforme configuração (modules.toml / settings)
    - Executar as atualizações através dos serviços de negócio de forma isolada
    - Permitir iniciar, pausar, retomar e encerrar o agendador

Uso:
    from scheduler.job_scheduler import job_scheduler

    await job_scheduler.start()
    ...
    await job_scheduler.stop()
"""

import asyncio
from typing import Any, Callable, Coroutine, Optional

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

from config.settings import settings
from core.event_bus import Events, event_bus
from core.module_manager import module_manager
from utils.logger import get_logger

logger = get_logger(__name__)


class JobScheduler:
    """
    Gerenciador do agendador em background.
    Usa BackgroundScheduler para rodar de forma transparente em conjunto com a GUI Tkinter.
    """

    def __init__(self) -> None:
        self._scheduler: Optional[BackgroundScheduler] = None
        self._running: bool = False
        self._registered_jobs: dict[str, str] = {}  # module_name -> job_id

    def start(self) -> None:
        """
        Inicializa e inicia o BackgroundScheduler.
        """
        if self._running:
            logger.warning("JobScheduler já está em execução")
            return

        self._scheduler = BackgroundScheduler(
            timezone=settings.scheduler_timezone,
        )
        self._scheduler.start()
        self._running = True
        logger.info("JobScheduler iniciado com sucesso (fuso horário: {tz})", tz=settings.scheduler_timezone)

    def stop(self) -> None:
        """
        Para o agendador e remove todos os jobs ativos.
        """
        if not self._running or self._scheduler is None:
            return

        try:
            self._scheduler.shutdown(wait=False)
        except Exception as e:
            logger.error("Erro ao encerrar JobScheduler: {err}", err=str(e))

        self._running = False
        self._scheduler = None
        self._registered_jobs.clear()
        logger.info("JobScheduler encerrado")

    def add_module_job(
        self,
        module_name: str,
        update_func: Callable[[], Coroutine[Any, Any, Any]],
        interval_seconds: int,
    ) -> bool:
        """
        Adiciona ou atualiza um job periódico para um módulo.

        Args:
            module_name: Nome do módulo (ex: "aircraft").
            update_func: Função assíncrona executada no intervalo.
            interval_seconds: Intervalo em segundos entre execuções.

        Returns:
            True se adicionado com sucesso, False caso contrário.
        """
        if not self._running or self._scheduler is None:
            logger.error("Não é possível adicionar job: JobScheduler não está rodando")
            return False

        # Se já existe um job para o módulo, remove primeiro
        if module_name in self._registered_jobs:
            self.remove_module_job(module_name)

        job_id = f"job_module_{module_name}"

        import inspect

        # Se a função de update for assíncrona, encapsula com asyncio.run para execução em thread de background
        if inspect.iscoroutinefunction(update_func):
            def target_func():
                asyncio.run(update_func())
        else:
            target_func = update_func

        try:
            self._scheduler.add_job(
                func=target_func,
                trigger=IntervalTrigger(seconds=interval_seconds),
                id=job_id,
                name=f"Update Job for {module_name}",
                replace_existing=True,
                max_instances=1,
            )
            self._registered_jobs[module_name] = job_id
            logger.info(
                "JobScheduler: registrado job '{job}' para módulo '{mod}' a cada {interval}s",
                job=job_id,
                mod=module_name,
                interval=interval_seconds,
            )
            return True
        except Exception as e:
            logger.error(
                "JobScheduler: erro ao adicionar job para módulo '{mod}': {err}",
                mod=module_name,
                err=str(e),
            )
            return False

    def remove_module_job(self, module_name: str) -> bool:
        """
        Remove o job agendado de um módulo.

        Args:
            module_name: Nome do módulo.

        Returns:
            True se removido, False caso contrário.
        """
        if not self._running or self._scheduler is None:
            return False

        job_id = self._registered_jobs.get(module_name)
        if not job_id:
            return False

        try:
            self._scheduler.remove_job(job_id)
            del self._registered_jobs[module_name]
            logger.info("JobScheduler: removido job do módulo '{mod}'", mod=module_name)
            return True
        except Exception as e:
            logger.error("JobScheduler: erro ao remover job do módulo '{mod}': {err}", mod=module_name, err=str(e))
            return False

    @property
    def is_running(self) -> bool:
        """Retorna True se o agendador está rodando."""
        return self._running

    def get_status(self) -> dict[str, Any]:
        """
        Retorna o status atual de jobs agendados.
        """
        return {
            "running": self._running,
            "jobs_count": len(self._registered_jobs),
            "jobs": list(self._registered_jobs.keys()),
        }


# Singleton global do agendador
job_scheduler: JobScheduler = JobScheduler()
