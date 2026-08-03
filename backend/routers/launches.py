"""
AeroTracker Core — Launches Router
====================================
Endpoints REST para lançamentos espaciais.

REST:
    GET  /api/v1/launches     → próximos lançamentos espaciais
"""

import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request

from services.launch_service import LaunchService

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Launches"])


def get_launch_service(request: Request) -> LaunchService:
    return request.app.state.launch_service


ServiceDep = Annotated[LaunchService, Depends(get_launch_service)]


@router.get(
    "/launches",
    summary="Próximos lançamentos espaciais",
    description="Retorna a lista de próximos lançamentos via Launch Library 2.",
)
async def get_launches(service: ServiceDep):
    data = service.last_data
    if data is None:
        raise HTTPException(status_code=204, detail="Dados de lançamentos ainda não disponíveis.")

    # LaunchService retorna lista ou modelo — tratar ambos
    if hasattr(data, "model_dump"):
        payload = data.model_dump()
    elif isinstance(data, list):
        payload = {"launches": [
            item.model_dump() if hasattr(item, "model_dump") else item
            for item in data
        ]}
    else:
        payload = {"launches": [], "raw": str(data)}

    return {"status": "ok", **payload}
