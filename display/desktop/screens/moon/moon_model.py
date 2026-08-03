"""
AeroTracker Core — Moon Model (MVC)
===================================
Modelo de dados astronômicos do módulo Lunar.
"""

from PySide6.QtCore import QObject, Signal


class MoonModel(QObject):
    """
    Model da tela Moon.
    """

    data_changed = Signal()

    def __init__(self) -> None:
        super().__init__()
        self._title_text = "🌙 LUNAR EPHEMERIS — RASTREADOR LUNAR"
        self._phase_name = "Waxing Gibbous"
        self._illumination = "91.4%"
        self._distance_km = "384,400 km"
        self._next_full_moon = "In 4 Days"

    @property
    def title_text(self) -> str:
        return self._title_text

    @property
    def phase_name(self) -> str:
        return self._phase_name

    @property
    def illumination(self) -> str:
        return self._illumination

    @property
    def distance_km(self) -> str:
        return self._distance_km

    @property
    def next_full_moon(self) -> str:
        return self._next_full_moon

    def update_moon(self, phase: str, illum: str, dist: str) -> None:
        self._phase_name = phase
        self._illumination = illum
        self._distance_km = dist
        self.data_changed.emit()
