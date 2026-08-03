"""
AeroTracker Core — Weather Router
===================================
Endpoints REST e WebSocket para o módulo meteorológico.

REST:
    GET  /api/v1/weather           → clima atual
    GET  /api/v1/weather/forecast  → previsão de 5 dias

WebSocket:
    WS   /api/v1/ws/weather        → atualizações em tempo real
"""

import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, WebSocket, WebSocketDisconnect

from backend.websocket.manager import ws_manager
from services.weather_service import WeatherService

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Weather"])


def get_weather_service(request: Request) -> WeatherService:
    return request.app.state.weather_service


ServiceDep = Annotated[WeatherService, Depends(get_weather_service)]


@router.get(
    "/weather",
    summary="Clima atual",
    description="Retorna o snapshot meteorológico mais recente para SBGR (Guarulhos).",
)
async def get_weather(service: ServiceDep):
    data = service.last_data
    if data is None:
        raise HTTPException(status_code=204, detail="Dados meteorológicos ainda não disponíveis.")

    return {
        "status": "ok",
        "data": data.model_dump(),
    }


@router.get(
    "/weather/forecast",
    summary="Previsão de 5 dias",
    description="Busca previsão meteorológica de 5 dias / 3h diretamente na API.",
)
async def get_forecast(service: ServiceDep):
    try:
        forecast = await service.get_forecast()
        return {"status": "ok", "data": forecast.model_dump()}
    except Exception as e:
        logger.error("[Weather] Erro ao buscar previsão: %s", e)
        raise HTTPException(status_code=503, detail=f"Serviço de previsão indisponível: {e}")


@router.websocket("/ws/weather")
async def ws_weather(websocket: WebSocket):
    """WebSocket de clima em tempo real."""
    await ws_manager.connect(websocket, channel="weather")
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket, channel="weather")
