"""
AeroTracker Core — Dashboard Controller
========================================
Controlador MVC do Dashboard. Consome os Services e o EventBus
para atualizar o DashboardModel. Nunca consome APIs diretamente.
"""

from PySide6.QtCore import QObject
from core.event_bus import Event, Events, event_bus
from core.module_manager import module_manager
from display.desktop.screens.dashboard.dashboard_model import DashboardModel


class DashboardController(QObject):
    """
    Controller do Dashboard que intermedia dados dos Services com o Model.
    """

    def __init__(self, model: DashboardModel) -> None:
        super().__init__()
        self.model = model

        # Inscreve nos eventos do sistema
        event_bus.subscribe(Events.AIRCRAFT_UPDATED, handler=self._on_aircraft_updated)
        event_bus.subscribe(Events.WEATHER_UPDATED, handler=self._on_weather_updated)

        self.update_status()

    def update_status(self) -> None:
        """Atualiza a contagem de módulos ativos."""
        st = module_manager.status()
        self.model.update_modules_status(st["active"], st["total"])

    def _on_aircraft_updated(self, event: Event) -> None:
        data = event.data
        if not data:
            return

        count = 0
        if hasattr(data, "total_count"):
            count = data.total_count
        elif isinstance(data, dict):
            count = len(data.get("aircraft", []))

        self.model.update_aircraft_count(count)

    def _on_weather_updated(self, event: Event) -> None:
        data = event.data
        if not data:
            return

        temp = getattr(data, "temperature_c", None) or (data.get("temperature_c") if isinstance(data, dict) else 0.0)
        cond = "Normal"
        if hasattr(data, "condition") and data.condition:
            cond = data.condition.description
        elif isinstance(data, dict):
            cond = data.get("condition", {}).get("description", "Normal")

        self.model.update_weather_temp(temp, cond)
