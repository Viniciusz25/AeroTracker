"""
AeroTracker Core — Aircraft Controller (MVC)
============================================
Controlador do Radar de Aeronaves. Intermedia entre AircraftService e AircraftModel.
"""

import asyncio
import threading
from PySide6.QtCore import QObject
from core.event_bus import Event, Events, event_bus
from display.desktop.screens.aircraft.aircraft_model import AircraftModel
from utils.logger import get_logger

logger = get_logger(__name__)


class AircraftController(QObject):
    """
    Controller do Radar de Aeronaves.
    """

    def __init__(self, model: AircraftModel, service=None) -> None:
        super().__init__()
        self.model = model
        self.service = service

        # Inscreve no EventBus
        event_bus.subscribe(Events.AIRCRAFT_UPDATED, handler=self._on_aircraft_updated)

        # Se o serviço tiver dados anteriores, carrega no Model
        if self.service and self.service.last_data:
            self.model.update_data(self.service.last_data)

    def trigger_manual_update(self) -> None:
        """Dispara atualização manual via Service em thread de segundo plano."""
        if not self.service:
            return

        self.model.set_status_message("⏳ Conectando à API OpenSky Network...")

        def _worker():
            try:
                asyncio.run(self.service.update())
            except Exception as e:
                logger.error("Erro na atualização do serviço de aeronaves: {err}", err=str(e))

        threading.Thread(target=_worker, daemon=True).start()

    def _on_aircraft_updated(self, event: Event) -> None:
        data = event.data
        if data is not None:
            self.model.update_data(data)
