"""
AeroTracker Core — WorldMap Controller (MVC)
============================================
Controller da tela de Mapa Mundial.
"""

from PySide6.QtCore import QObject
from core.event_bus import Event, Events, event_bus
from display.desktop.screens.world_map.world_map_model import WorldMapModel


class WorldMapController(QObject):
    """
    Controller do Mapa Mundial.
    """

    def __init__(self, model: WorldMapModel) -> None:
        super().__init__()
        self.model = model
        event_bus.subscribe(Events.AIRCRAFT_UPDATED, handler=self._on_aircraft)
        event_bus.subscribe(Events.ISS_POSITION_UPDATED, handler=self._on_iss)

    def _on_aircraft(self, event: Event) -> None:
        count = len(event.data.aircraft) if hasattr(event.data, "aircraft") else 0
        self.model.update_telemetry(count, self.model.iss_lat_lon)

    def _on_iss(self, event: Event) -> None:
        pos = getattr(event.data, "position", None)
        pos_str = f"ISS: {pos.latitude:.2f}°, {pos.longitude:.2f}°" if pos else "ISS: Tracking..."
        self.model.update_telemetry(self.model.active_flights, pos_str)
