"""
AeroTracker Core — Aircraft Router
====================================
Endpoints REST e WebSocket para o módulo de aeronaves.

REST:
    GET  /api/v1/aircraft               → snapshot atual de aeronaves
    GET  /api/v1/aircraft/{icao24}      → aeronave específica por ICAO24

WebSocket:
    WS   /api/v1/ws/aircraft            → stream em tempo real (3s)
"""

import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, WebSocket, WebSocketDisconnect

from backend.websocket.manager import ws_manager
from services.aircraft_service import AircraftService

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Aircraft"])


def get_aircraft_service(request: Request) -> AircraftService:
    """Injeção de dependência — retorna o singleton do AircraftService."""
    return request.app.state.aircraft_service


ServiceDep = Annotated[AircraftService, Depends(get_aircraft_service)]


# ---------------------------------------------------------------------------
# REST Endpoints
# ---------------------------------------------------------------------------

@router.get(
    "/aircraft",
    summary="Lista aeronaves no radar",
    description="Retorna o último snapshot de aeronaves dentro do raio configurado (10km de SBGR).",
    response_description="Lista de aeronaves com metadados",
)
async def get_aircraft(service: ServiceDep):
    """
    Retorna os dados em cache da última atualização.

    204 se o serviço ainda não fez a primeira busca.
    """
    data = service.last_data

    if data is None:
        raise HTTPException(
            status_code=204,
            detail="Serviço ainda não inicializado. Aguarde o primeiro ciclo do scheduler.",
        )

    return {
        "status": "ok",
        "total_count": data.total_count,
        "airborne_count": data.airborne_count,
        "on_ground_count": data.on_ground_count,
        "query_time": data.query_time,
        "aircraft": [a.model_dump() for a in data.aircraft],
    }


@router.get(
    "/aircraft/{icao24}",
    summary="Busca aeronave por ICAO24",
    description="Busca diretamente no OpenSky uma aeronave específica pelo código ICAO24.",
)
async def get_aircraft_by_icao(icao24: str, service: ServiceDep):
    """Busca ao vivo uma aeronave pelo identificador ICAO24 (6 caracteres hex)."""
    if len(icao24) != 6:
        raise HTTPException(status_code=422, detail="icao24 deve ter exatamente 6 caracteres hex")

    aircraft = await service.get_aircraft_by_icao(icao24.lower())

    if aircraft is None:
        raise HTTPException(status_code=404, detail=f"Aeronave '{icao24}' não encontrada")

    return {"status": "ok", "aircraft": aircraft.model_dump()}


# ---------------------------------------------------------------------------
# WebSocket
# ---------------------------------------------------------------------------

@router.websocket("/ws/aircraft")
async def ws_aircraft(websocket: WebSocket):
    """
    WebSocket de aeronaves em tempo real.

    Recebe broadcasts da bridge EventBus → WebSocket cada vez que o
    AircraftService atualiza os dados (configurável em modules.toml).
    """
    await ws_manager.connect(websocket, channel="aircraft")
    try:
        while True:
            # Mantém a conexão ativa aguardando mensagens do cliente
            # (pings, filtros futuros, etc.)
            await websocket.receive_text()
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket, channel="aircraft")
        logger.info("[WS] Cliente desconectado do canal 'aircraft'")
