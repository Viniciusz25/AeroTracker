"""
AeroTracker Core — SolarSystem Controller (MVC)
================================================
Controller do Sistema Solar.
"""

from PySide6.QtCore import QObject
from display.desktop.screens.solar_system.solar_system_model import SolarSystemModel


class SolarSystemController(QObject):
    """
    Controller da tela Solar System.
    """

    def __init__(self, model: SolarSystemModel) -> None:
        super().__init__()
        self.model = model
