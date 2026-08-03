"""
AeroTracker Core — Pacote Core
================================
Exporta os componentes centrais da aplicação.
"""

from core.app import AeroTrackerApp
from core.event_bus import Event, EventBus, Events, event_bus
from core.module_manager import ModuleInfo, ModuleManager, ModuleState, module_manager

__all__ = [
    # App bootstrap
    "AeroTrackerApp",
    # Event Bus
    "event_bus",
    "EventBus",
    "Event",
    "Events",
    # Module Manager
    "module_manager",
    "ModuleManager",
    "ModuleInfo",
    "ModuleState",
]
