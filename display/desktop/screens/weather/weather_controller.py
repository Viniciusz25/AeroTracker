"""
AeroTracker Core — Weather Controller (MVC)
===========================================
Controlador da tela de Clima. Intermedia entre WeatherService/EventBus e o WeatherModel.
"""

import asyncio
import threading
from PySide6.QtCore import QObject
from core.event_bus import Event, Events, event_bus
from display.desktop.screens.weather.weather_model import WeatherModel
from utils.logger import get_logger

logger = get_logger(__name__)


class WeatherController(QObject):
    """
    Controller do módulo de Clima.
    """

    def __init__(self, model: WeatherModel, service=None) -> None:
        super().__init__()
        self.model = model
        self.service = service

        # Inscreve no EventBus
        event_bus.subscribe(Events.WEATHER_UPDATED, handler=self._on_weather_updated)

        if self.service and self.service.last_data:
            self.model.update_data(self.service.last_data)

    def trigger_manual_update(self) -> None:
        """Dispara atualização manual via Service em thread de segundo plano."""
        if not self.service:
            return

        def _worker():
            try:
                asyncio.run(self.service.update())
            except Exception as e:
                logger.error("Erro na atualização manual do clima: {err}", err=str(e))

        threading.Thread(target=_worker, daemon=True).start()

    def _on_weather_updated(self, event: Event) -> None:
        data = event.data
        if data is not None:
            self.model.update_data(data)
