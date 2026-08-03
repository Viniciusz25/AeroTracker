"""
AeroTracker Core — NASA Router
================================
Endpoints REST para dados da NASA.

REST:
    GET  /api/v1/nasa/apod     → Astronomy Picture of the Day
"""

import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request

from services.nasa_service import NASAService

logger = logging.getLogger(__name__)
router = APIRouter(tags=["NASA"])


def get_nasa_service(request: Request) -> NASAService:
    return request.app.state.nasa_service


ServiceDep = Annotated[NASAService, Depends(get_nasa_service)]


@router.get(
    "/nasa/apod",
    summary="NASA APOD",
    description="Retorna a Imagem Astronômica do Dia (Astronomy Picture of the Day).",
)
async def get_apod(service: ServiceDep):
    data = service.last_data
    if data is None:
        raise HTTPException(status_code=204, detail="Dados NASA APOD ainda não disponíveis.")

    return {
        "status": "ok",
        "data": data.model_dump() if hasattr(data, "model_dump") else data,
    }
