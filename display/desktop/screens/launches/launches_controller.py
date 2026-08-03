"""
AeroTracker Core — Launches Controller (MVC)
============================================
Controller de lançamentos espaciais. Intermedia entre LaunchService e LaunchesModel.
"""

import asyncio
import threading
from PySide6.QtCore import QObject
from core.event_bus import Event, Events, event_bus
from display.desktop.screens.launches.launches_model import LaunchesModel
from utils.logger import get_logger

logger = get_logger(__name__)


class LaunchesController(QObject):
    """
    Controller da tela Launches.
    """

    def __init__(self, model: LaunchesModel, service=None) -> None:
        super().__init__()
        self.model = model
        self.service = service

        event_bus.subscribe(Events.LAUNCH_UPDATED, handler=self._on_launch_updated)

        if self.service and self.service.last_data:
            self.model.update_launches(self.service.last_data)

    def trigger_manual_update(self) -> None:
        if not self.service:
            return

        def _worker():
            try:
                asyncio.run(self.service.update())
            except Exception as e:
                logger.error("Erro na atualização de lançamentos: {err}", err=str(e))

        threading.Thread(target=_worker, daemon=True).start()

    def _on_launch_updated(self, event: Event) -> None:
        if event.data is not None:
            self.model.update_launches(event.data)
