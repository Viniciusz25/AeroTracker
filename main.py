"""
AeroTracker Core — Ponto de Entrada Principal
==============================================
Orquestrador central da aplicação AeroTracker Core.

Fluxo de Execução:
    1. Inicialização dos subsistemas de bootstrap (AeroTrackerApp)
    2. Instanciação e injeção de serviços de negócio
    3. Inicialização do agendador em segundo plano (JobScheduler)
    4. Carga inicial dos dados dos módulos em threads de background
    5. Execução da interface de usuário Desktop (CustomTkinter)
    6. Housekeeping e shutdown gracioso ao fechar a aplicação
"""

import asyncio
import sys
import threading
from pathlib import Path

# Adiciona o diretório raiz ao sys.path para garantir imports absolutos
_PROJECT_ROOT = Path(__file__).parent.resolve()
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from core.app import AeroTrackerApp
from core.module_manager import module_manager
from display.desktop.app_window import MainWindow
from scheduler.job_scheduler import job_scheduler
from services.aircraft_service import AircraftService
from services.iss_service import ISSService
from services.launch_service import LaunchService
from services.nasa_service import NASAService
from services.weather_service import WeatherService
from utils.logger import get_logger

logger = get_logger(__name__)


def _run_initial_fetch(service) -> None:
    """Executa primeira busca de dados em thread de background."""
    def _worker():
        try:
            asyncio.run(service.update())
        except Exception as e:
            logger.error("Erro na busca inicial do serviço '{mod}': {err}", mod=service.module_name, err=str(e))

    threading.Thread(target=_worker, daemon=True).start()


def main() -> None:
    """Ponto de entrada síncrono para inicialização e execução da UI."""
    logger.info("Iniciando AeroTracker Core...")

    # 1. Bootstrap da aplicação
    app = AeroTrackerApp()
    app.initialize()

    # Instanciação dos serviços
    aircraft_service = AircraftService()
    weather_service = WeatherService()
    iss_service = ISSService()
    launch_service = LaunchService()
    nasa_service = NASAService()

    services = {
        "aircraft": aircraft_service,
        "weather": weather_service,
        "iss": iss_service,
        "launch": launch_service,
        "nasa": nasa_service,
    }

    # 2. Inicialização do JobScheduler
    job_scheduler.start()

    # Registrar rotinas dos módulos ativos no JobScheduler
    if module_manager.is_active("aircraft"):
        job_scheduler.add_module_job(
            "aircraft",
            aircraft_service.update,
            interval_seconds=module_manager.get("aircraft").interval_seconds,
        )
        _run_initial_fetch(aircraft_service)

    if module_manager.is_active("weather"):
        job_scheduler.add_module_job(
            "weather",
            weather_service.update,
            interval_seconds=module_manager.get("weather").interval_seconds,
        )
        _run_initial_fetch(weather_service)

    if module_manager.is_active("iss"):
        job_scheduler.add_module_job(
            "iss",
            iss_service.update,
            interval_seconds=module_manager.get("iss").interval_seconds,
        )
        _run_initial_fetch(iss_service)

    if module_manager.is_active("launch"):
        job_scheduler.add_module_job(
            "launch",
            launch_service.update,
            interval_seconds=module_manager.get("launch").interval_seconds,
        )
        _run_initial_fetch(launch_service)

    if module_manager.is_active("nasa"):
        job_scheduler.add_module_job(
            "nasa",
            nasa_service.update,
            interval_seconds=module_manager.get("nasa").interval_seconds,
        )
        _run_initial_fetch(nasa_service)

    # 3. Execução da Janela Desktop
    try:
        window = MainWindow(services=services)
        window.mainloop()
    except Exception as e:
        logger.error("Erro durante execução da janela principal: {err}", err=str(e))
    finally:
        # Encerramento gracioso
        logger.info("Encerrando AeroTracker Core...")
        job_scheduler.stop()
        app.shutdown()


if __name__ == "__main__":
    main()
