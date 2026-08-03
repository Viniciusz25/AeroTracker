"""
AeroTracker Core — Backend FastAPI
===================================
Ponto de entrada da API FastAPI.

Gerencia o ciclo de vida da aplicação:
    - Startup: inicializa core, serviços, scheduler e WebSocket bridge
    - Runtime: serve endpoints REST e WebSocket
    - Shutdown: encerramento gracioso de todos os subsistemas
"""

import asyncio
import sys
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Garante que o projeto raiz está no sys.path
_PROJECT_ROOT = Path(__file__).parent.parent.resolve()
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from core.app import AeroTrackerApp
from core.module_manager import module_manager
from scheduler.job_scheduler import job_scheduler
from services.aircraft_service import AircraftService
from services.iss_service import ISSService
from services.launch_service import LaunchService
from services.nasa_service import NASAService
from services.weather_service import WeatherService
from utils.logger import get_logger

from backend.websocket.events import start_event_bridge
from backend.routers import aircraft, iss, launches, nasa, system, weather

logger = get_logger(__name__)

# ---------------------------------------------------------------------------
# Singletons de serviço — compartilhados entre routers e WebSocket bridge
# ---------------------------------------------------------------------------
aircraft_service = AircraftService()
weather_service = WeatherService()
iss_service = ISSService()
launch_service = LaunchService()
nasa_service = NASAService()


def _schedule_service(name: str, service) -> None:
    """Registra um serviço no JobScheduler se o módulo estiver ativo."""
    if module_manager.is_active(name):
        job_scheduler.add_module_job(
            name,
            service.update,
            interval_seconds=module_manager.get(name).interval_seconds,
        )
        # Dispara busca inicial em background
        asyncio.create_task(service.update())
        logger.info("[Backend] Módulo '{name}' agendado", name=name)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gerencia startup e shutdown do ciclo de vida FastAPI."""
    logger.info("=" * 60)
    logger.info("  AeroTracker Core v2.0 — Backend FastAPI iniciando...")
    logger.info("=" * 60)

    # 1. Bootstrap dos subsistemas (Settings, Cache, Storage, EventBus, Modules)
    core_app = AeroTrackerApp()
    core_app.initialize()

    # 2. Scheduler de background jobs
    job_scheduler.start()

    # 3. Agendar atualizações periódicas por módulo
    _schedule_service("aircraft", aircraft_service)
    _schedule_service("weather", weather_service)
    _schedule_service("iss", iss_service)
    _schedule_service("launch", launch_service)
    _schedule_service("nasa", nasa_service)

    # 4. Bridge EventBus → WebSocket (publica eventos em tempo real)
    start_event_bridge()

    logger.info("[Backend] Startup completo. API disponível em http://localhost:8000")
    logger.info("[Backend] Docs interativos em http://localhost:8000/docs")

    yield  # Aplicação em execução

    # Shutdown gracioso
    logger.info("[Backend] Encerrando AeroTracker Core...")
    job_scheduler.stop()
    core_app.shutdown()
    logger.info("[Backend] Shutdown concluído.")


# ---------------------------------------------------------------------------
# Aplicação FastAPI
# ---------------------------------------------------------------------------
app = FastAPI(
    title="AeroTracker Core API",
    description="Real-time aerospace monitoring API — Aircraft, ISS, Weather, Launches, NASA",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS — permite frontend Vite (dev) e Tauri (prod)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",    # Vite dev server
        "http://localhost:1420",    # Tauri dev
        "tauri://localhost",        # Tauri prod
        "https://tauri.localhost",  # Tauri prod (Windows)
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Injeção de serviços nos routers via estado da app
# ---------------------------------------------------------------------------
app.state.aircraft_service = aircraft_service
app.state.weather_service = weather_service
app.state.iss_service = iss_service
app.state.launch_service = launch_service
app.state.nasa_service = nasa_service

# ---------------------------------------------------------------------------
# Routers
# ---------------------------------------------------------------------------
app.include_router(aircraft.router, prefix="/api/v1")
app.include_router(weather.router, prefix="/api/v1")
app.include_router(iss.router, prefix="/api/v1")
app.include_router(launches.router, prefix="/api/v1")
app.include_router(nasa.router, prefix="/api/v1")
app.include_router(system.router, prefix="/api/v1")


@app.get("/", include_in_schema=False)
async def root():
    return {"status": "ok", "message": "AeroTracker Core API v2.0", "docs": "/docs"}
