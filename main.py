"""
AeroTracker Core — Ponto de Entrada Principal (PySide6 / Qt)
============================================================
Orquestrador central da aplicação AeroTracker Core.

Fluxo de Execução:
    1. Inicialização do QApplication (PySide6)
    2. Configuração de Exception Handler global para proteger a UI contra fechamentos abruptos
    3. Bootstrap dos subsistemas de infraestrutura (AeroTrackerApp)
    4. Instanciação e injeção de serviços de negócio
    5. Inicialização do agendador em segundo plano (JobScheduler)
    6. Carga inicial dos dados dos módulos em threads de background
    7. Execução da janela principal (MainWindow em MVC)
    8. Housekeeping e shutdown gracioso ao fechar o app
"""

import asyncio
import sys
import threading
from pathlib import Path

# Adiciona o diretório raiz ao sys.path para garantir imports absolutos
_PROJECT_ROOT = Path(__file__).parent.resolve()
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from PySide6.QtWidgets import QApplication

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


def _handle_exception(exc_type, exc_value, exc_traceback):
    """Captura e registra exceções não tratadas sem derrubar o processo."""
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    logger.critical("Exceção não tratada no Qt Event Loop: {err}", err=exc_value, exc_info=(exc_type, exc_value, exc_traceback))


sys.excepthook = _handle_exception


def _run_initial_fetch(service) -> None:
    """Executa primeira busca de dados em thread de background."""
    def _worker():
        try:
            asyncio.run(service.update())
        except Exception as e:
            logger.error("Erro na busca inicial do serviço '{mod}': {err}", mod=service.module_name, err=str(e))

    threading.Thread(target=_worker, daemon=True).start()


def main() -> None:
    """Ponto de entrada principal para inicialização e execução da aplicação Qt."""
    logger.info("Iniciando AeroTracker Core (PySide6 Qt Engine)...")

    # 1. Aplicação Qt
    qt_app = QApplication(sys.argv)

    # 2. Bootstrap dos subsistemas
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

    # 3. Inicialização do JobScheduler
    job_scheduler.start()

    # Registrar rotinas dos módulos ativos no JobScheduler e efetuar busca inicial
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

    # 4. Execução da Janela Desktop (PySide6 / MVC)
    window = MainWindow(services=services)
    window.show()

    exit_code = qt_app.exec()

    # 5. Encerramento gracioso
    logger.info("Encerrando AeroTracker Core...")
    job_scheduler.stop()
    app.shutdown()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
