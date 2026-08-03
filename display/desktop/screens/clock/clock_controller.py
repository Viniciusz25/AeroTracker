"""
AeroTracker Core — Clock Controller (MVC)
=========================================
Controller da tela de relógio aeroespacial.
"""

from PySide6.QtCore import QObject
from display.desktop.screens.clock.clock_model import ClockModel


class ClockController(QObject):
    """
    Controller da tela Clock.
    """

    def __init__(self, model: ClockModel) -> None:
        super().__init__()
        self.model = model
