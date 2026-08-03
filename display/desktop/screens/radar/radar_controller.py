"""
AeroTracker Core — Radar Controller (MVC)
=========================================
Controlador da tela de Radar ATC. Intermedia entre AircraftService e RadarModel.
"""

import asyncio
import threading
from PySide6.QtCore import QObject
from core.event_bus import Event, Events, event_bus
from display.desktop.screens.radar.radar_model import RadarModel
from utils.logger import get_logger

logger = get_logger(__name__)


class RadarController(QObject):
    """
    Controller da tela de Radar ATC.
    """

    def __init__(self, model: RadarModel, service=None) -> None:
        super().__init__()
        self.model = model
        self.service = service

        event_bus.subscribe(Events.AIRCRAFT_UPDATED, handler=self._on_aircraft_updated)

        if self.service and self.service.last_data:
            self.model.update_data(self.service.last_data)

    def trigger_manual_update(self) -> None:
        if not self.service:
            return

        def _worker():
            try:
                asyncio.run(self.service.update())
            except Exception as e:
                logger.error("Erro na atualização do radar: {err}", err=str(e))

        threading.Thread(target=_worker, daemon=True).start()

    def _on_aircraft_updated(self, event: Event) -> None:
        if event.data is not None:
            self.model.update_data(event.data)
