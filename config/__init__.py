"""
AeroTracker Core — Pacote de Configuração
==========================================
Exporta os singletons principais de configuração.
"""

from config.module_config import ModulesConfig, module_config
from config.settings import AppSettings, settings

__all__ = [
    "settings",
    "AppSettings",
    "module_config",
    "ModulesConfig",
]
