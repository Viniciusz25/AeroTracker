"""
AeroTracker Core — ISS Router
================================
Endpoints REST e WebSocket para rastreamento da ISS.

REST:
    GET  /api/v1/iss     → posição atual da ISS

WebSocket:
    WS   /api/v1/ws/iss  → stream em tempo real (5s)
"""

import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, WebSocket, WebSocketDisconnect

from backend.websocket.manager import ws_manager
from services.iss_service import ISSService

logger = logging.getLogger(__name__)
router = APIRouter(tags=["ISS"])


def get_iss_service(request: Request) -> ISSService:
    return request.app.state.iss_service


ServiceDep = Annotated[ISSService, Depends(get_iss_service)]


@router.get(
    "/iss",
    summary="Posição atual da ISS",
    description="Retorna a posição orbital mais recente da Estação Espacial Internacional.",
)
async def get_iss(service: ServiceDep):
    data = service.last_data
    if data is None:
        raise HTTPException(status_code=204, detail="Posição da ISS ainda não disponível.")

    return {
        "status": "ok",
        "data": data.model_dump() if hasattr(data, "model_dump") else data,
    }


@router.websocket("/ws/iss")
async def ws_iss(websocket: WebSocket):
    """WebSocket de posição da ISS em tempo real (atualiza a cada 5s)."""
    await ws_manager.connect(websocket, channel="iss")
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket, channel="iss")
