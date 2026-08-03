"""
AeroTracker Core — Pacote de Clientes de Aeronaves
======================================================
Exporta os adapters de API de rastreamento de aeronaves.
"""

from api.aircraft.opensky_client import OpenSkyClient

__all__ = [
    "OpenSkyClient",
]
