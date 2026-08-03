"""
AeroTracker Core — Settings Controller (MVC)
============================================
Controller de configurações.
"""

from PySide6.QtCore import QObject
from display.desktop.screens.settings.settings_model import SettingsModel


class SettingsController(QObject):
    """
    Controller da tela Settings.
    """

    def __init__(self, model: SettingsModel) -> None:
        super().__init__()
        self.model = model
