"""
AeroTracker Core — Aircraft Details Controller (MVC)
===================================================
Controller de detalhes da aeronave.
"""

from PySide6.QtCore import QObject
from display.desktop.screens.aircraft_details.details_model import AircraftDetailsModel


class AircraftDetailsController(QObject):
    """
    Controller da tela Aircraft Details.
    """

    def __init__(self, model: AircraftDetailsModel) -> None:
        super().__init__()
        self.model = model
