"""
AeroTracker Core — Pacote de Utilitários
==========================================
Exporta utilitários globais da aplicação.
"""

from utils.logger import get_logger, setup_logging

__all__ = [
    "get_logger",
    "setup_logging",
]
