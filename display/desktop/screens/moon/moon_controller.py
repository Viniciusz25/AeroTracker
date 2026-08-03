"""
AeroTracker Core — Moon Controller (MVC)
========================================
Controller do módulo Lunar.
"""

from PySide6.QtCore import QObject
from display.desktop.screens.moon.moon_model import MoonModel


class MoonController(QObject):
    """
    Controller da tela Moon.
    """

    def __init__(self, model: MoonModel) -> None:
        super().__init__()
        self.model = model
