"""
AeroTracker Core — Settings Model (MVC)
=======================================
Modelo de configurações do sistema.
"""

from PySide6.QtCore import QObject, Signal


class SettingsModel(QObject):
    """
    Model da tela Settings.
    """

    data_changed = Signal()

    def __init__(self) -> None:
        super().__init__()
        self._title_text = "⚙ SYSTEM CONFIGURATION — CONFIGURAÇÕES DE NAVEGAÇÃO"
        self._units_text = "Metric (Meters, km/h)"
        self._api_status_text = "ALL APIS ONLINE (5/5)"

    @property
    def title_text(self) -> str:
        return self._title_text

    @property
    def units_text(self) -> str:
        return self._units_text

    @property
    def api_status_text(self) -> str:
        return self._api_status_text
