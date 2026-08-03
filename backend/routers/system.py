"""
AeroTracker Core — System Router
==================================
Endpoints de saúde, diagnóstico e status dos módulos.

REST:
    GET  /api/v1/health      → health check simplificado
    GET  /api/v1/status      → status completo (módulos, cache, location)
    GET  /api/v1/modules     → lista de módulos com status individual

WebSocket:
    WS   /api/v1/ws/system   → eventos de sistema (erros, health changes)
"""

import logging
from datetime import UTC, datetime

from fastapi import APIRouter, Request, WebSocket, WebSocketDisconnect

from backend.websocket.manager import ws_manager
from core.app import AeroTrackerApp
from core.module_manager import module_manager
from config.settings import settings
from cache.cache_manager import cache_manager
from core.event_bus import event_bus

logger = logging.getLogger(__name__)
router = APIRouter(tags=["System"])

# Timestamp de startup da API
_STARTUP_TIME = datetime.now(UTC)


def _uptime_seconds() -> int:
    return int((datetime.now(UTC) - _STARTUP_TIME).total_seconds())


@router.get(
    "/health",
    summary="Health check",
    description="Verificação rápida de saúde da API. Retorna 200 se o servidor está operacional.",
)
async def health():
    """Health check endpoint — usado por Tauri e load balancers."""
    active = module_manager.get_active_modules()
    return {
        "status": "ok",
        "version": "2.0.0",
        "uptime_seconds": _uptime_seconds(),
        "active_modules": len(active),
        "timestamp": datetime.now(UTC).isoformat(),
    }


@router.get(
    "/status",
    summary="Status completo da aplicação",
    description="Retorna status detalhado de todos os subsistemas: módulos, cache, event bus e localização.",
)
async def get_status():
    """Endpoint completo para a página de Diagnósticos."""
    modules = module_manager.status() if hasattr(module_manager, "status") else {}
    cache_stats = cache_manager.stats() if hasattr(cache_manager, "stats") else {}
    eb_stats = event_bus.stats() if hasattr(event_bus, "stats") else {}

    return {
        "status": "ok",
        "version": "2.0.0",
        "uptime_seconds": _uptime_seconds(),
        "location": {
            "name": settings.default_location_name,
            "latitude": settings.default_latitude,
            "longitude": settings.default_longitude,
            "timezone": settings.default_timezone,
        },
        "modules": modules,
        "cache": cache_stats,
        "event_bus": eb_stats,
        "websocket": ws_manager.stats(),
    }


@router.get(
    "/modules",
    summary="Lista de módulos",
    description="Retorna todos os módulos registrados com seu status individual.",
)
async def get_modules():
    """Retorna o catálogo de módulos com status de atividade."""
    all_modules = module_manager.get_all_modules() if hasattr(module_manager, "get_all_modules") else []

    modules_list = []
    for mod in all_modules:
        modules_list.append({
            "name": mod.name,
            "display_name": getattr(mod, "display_name", mod.name),
            "description": getattr(mod, "description", ""),
            "active": mod.is_active if hasattr(mod, "is_active") else False,
            "interval_seconds": getattr(mod, "interval_seconds", 60),
            "last_updated": getattr(mod, "last_updated", None),
            "error": getattr(mod, "error_message", None),
        })

    return {
        "status": "ok",
        "total": len(modules_list),
        "active": sum(1 for m in modules_list if m["active"]),
        "modules": modules_list,
    }


@router.websocket("/ws/system")
async def ws_system(websocket: WebSocket):
    """
    WebSocket de eventos de sistema.

    Recebe: erros de API, mudanças de status de módulo, eventos críticos.
    """
    await ws_manager.connect(websocket, channel="system")
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket, channel="system")
        logger.info("[WS] Cliente desconectado do canal 'system'")
