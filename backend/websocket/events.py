"""
AeroTracker Core — EventBus → WebSocket Bridge
================================================
Assina eventos do EventBus Python e os republica via WebSocket
para todos os clientes React conectados.

Canais WebSocket:
    "aircraft" ← Events.AIRCRAFT_UPDATED
    "iss"      ← Events.ISS_POSITION_UPDATED
    "weather"  ← Events.WEATHER_UPDATED
    "launch"   ← Events.LAUNCH_UPDATED
    "system"   ← Events.ERROR_API, Events.ERROR_CRITICAL, Events.APP_STOPPING

Uso:
    from backend.websocket.events import start_event_bridge
    start_event_bridge()  # Chamar uma vez no lifespan startup
"""

import asyncio
import logging
from datetime import UTC, datetime

from core.event_bus import Events, event_bus
from backend.websocket.manager import ws_manager

logger = logging.getLogger(__name__)


def _now_iso() -> str:
    """Retorna timestamp ISO 8601 UTC."""
    return datetime.now(UTC).isoformat()


def _safe_broadcast(channel: str, payload: dict) -> None:
    """
    Agenda um broadcast no event loop ativo.

    Os handlers do EventBus são executados em threads de background —
    asyncio.create_task() exige o loop ativo do asyncio.
    """
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            loop.create_task(ws_manager.broadcast(channel, payload))
    except RuntimeError:
        logger.warning("[WS Bridge] Sem event loop ativo para broadcast no canal '%s'", channel)


# ---------------------------------------------------------------------------
# Handlers por domínio
# ---------------------------------------------------------------------------

def _on_aircraft_updated(event) -> None:
    """Republica atualização de aeronaves para o canal 'aircraft'."""
    if event.data is None:
        return

    try:
        data = event.data.model_dump() if hasattr(event.data, "model_dump") else dict(event.data)
        # Adiciona campos calculados que o modelo expõe via @property
        aircraft_list = data.get("aircraft", [])
        payload = {
            "event": "aircraft.updated",
            "timestamp": _now_iso(),
            "source": "opensky",
            "data": {
                "aircraft": aircraft_list,
                "total_count": len(aircraft_list),
                "airborne_count": sum(1 for a in aircraft_list if not a.get("on_ground")),
                "on_ground_count": sum(1 for a in aircraft_list if a.get("on_ground")),
                "query_time": data.get("query_time"),
            },
        }
        _safe_broadcast("aircraft", payload)
        logger.debug("[WS Bridge] aircraft.updated → %d aeronaves", len(aircraft_list))
    except Exception as e:
        logger.error("[WS Bridge] Erro ao processar aircraft.updated: %s", e)


def _on_iss_updated(event) -> None:
    """Republica atualização de posição da ISS para o canal 'iss'."""
    if event.data is None:
        return

    try:
        data = event.data.model_dump() if hasattr(event.data, "model_dump") else dict(event.data)
        payload = {
            "event": "iss.updated",
            "timestamp": _now_iso(),
            "source": "wheretheiss",
            "data": data,
        }
        _safe_broadcast("iss", payload)
    except Exception as e:
        logger.error("[WS Bridge] Erro ao processar iss.position_updated: %s", e)


def _on_weather_updated(event) -> None:
    """Republica dados de clima para o canal 'weather'."""
    if event.data is None:
        return

    try:
        data = event.data.model_dump() if hasattr(event.data, "model_dump") else dict(event.data)
        payload = {
            "event": "weather.updated",
            "timestamp": _now_iso(),
            "source": "openweather",
            "data": data,
        }
        _safe_broadcast("weather", payload)
    except Exception as e:
        logger.error("[WS Bridge] Erro ao processar weather.updated: %s", e)


def _on_launch_updated(event) -> None:
    """Republica dados de lançamentos para o canal 'launch'."""
    if event.data is None:
        return

    try:
        data = event.data if isinstance(event.data, dict) else {}
        payload = {
            "event": "launch.updated",
            "timestamp": _now_iso(),
            "source": "launch_library",
            "data": data,
        }
        _safe_broadcast("launch", payload)
    except Exception as e:
        logger.error("[WS Bridge] Erro ao processar launch.updated: %s", e)


def _on_api_error(event) -> None:
    """Republica erros de API para o canal 'system'."""
    try:
        payload = {
            "event": "module.error",
            "timestamp": _now_iso(),
            "data": {
                "module": getattr(event, "source", "unknown"),
                "error": str(event.data) if event.data else "Unknown error",
            },
        }
        _safe_broadcast("system", payload)
    except Exception as e:
        logger.error("[WS Bridge] Erro ao processar error.api: %s", e)


# ---------------------------------------------------------------------------
# Inicialização
# ---------------------------------------------------------------------------

def start_event_bridge() -> None:
    """
    Registra todos os handlers no EventBus Python.

    Deve ser chamado UMA única vez durante o startup da aplicação FastAPI.
    """
    event_bus.subscribe(Events.AIRCRAFT_UPDATED, _on_aircraft_updated)
    event_bus.subscribe(Events.ISS_POSITION_UPDATED, _on_iss_updated)
    event_bus.subscribe(Events.WEATHER_UPDATED, _on_weather_updated)
    event_bus.subscribe(Events.LAUNCH_UPDATED, _on_launch_updated)
    event_bus.subscribe(Events.ERROR_API, _on_api_error)
    event_bus.subscribe(Events.ERROR_CRITICAL, _on_api_error)

    logger.info("[WS Bridge] EventBus → WebSocket bridge ativada (5 canais)")
