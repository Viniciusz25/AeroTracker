"""
AeroTracker Core — Tracker Controller (MVC)
===========================================
Controller intermediador para o módulo Tracker.
"""

from PySide6.QtCore import QObject
from display.desktop.screens.tracker.tracker_model import TrackerModel


class TrackerController(QObject):
    """
    Controller do módulo Tracker.
    """

    def __init__(self, model: TrackerModel) -> None:
        super().__init__()
        self.model = model

    def sync_flight(self) -> None:
        self.model.data_changed.emit()
