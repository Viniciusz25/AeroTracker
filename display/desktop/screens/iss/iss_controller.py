"""
AeroTracker Core — ISS Controller (MVC)
=======================================
Controller do rastreador da ISS. Intermedia entre ISSService e ISSModel.
"""

import asyncio
import threading
from PySide6.QtCore import QObject
from core.event_bus import Event, Events, event_bus
from display.desktop.screens.iss.iss_model import ISSModel
from utils.logger import get_logger

logger = get_logger(__name__)


class ISSController(QObject):
    """
    Controller da tela ISS.
    """

    def __init__(self, model: ISSModel, service=None) -> None:
        super().__init__()
        self.model = model
        self.service = service

        event_bus.subscribe(Events.ISS_POSITION_UPDATED, handler=self._on_iss_updated)

        if self.service and self.service.last_data:
            self.model.update_position(self.service.last_data)

    def trigger_manual_update(self) -> None:
        if not self.service:
            return

        def _worker():
            try:
                asyncio.run(self.service.update())
            except Exception as e:
                logger.error("Erro na atualização da ISS: {err}", err=str(e))

        threading.Thread(target=_worker, daemon=True).start()

    def _on_iss_updated(self, event: Event) -> None:
        if event.data is not None:
            self.model.update_position(event.data)
