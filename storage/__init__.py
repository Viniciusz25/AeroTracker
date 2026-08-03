"""
AeroTracker Core — Pacote de Storage
=======================================
Exporta o gerenciador de persistência local.
"""

from storage.local_storage import LocalStorage, local_storage

__all__ = [
    "local_storage",
    "LocalStorage",
]
