"""
AeroTracker Core — WorldMap Model (MVC)
=======================================
Modelo de dados do Mapa Mundial Global.
"""

from PySide6.QtCore import QObject, Signal


class WorldMapModel(QObject):
    """
    Model da tela de Mapa Mundial.
    """

    data_changed = Signal()

    def __init__(self) -> None:
        super().__init__()
        self._title_text = "🌍 GLOBAL PROJECTION MAP — NAVEGAÇÃO MUNDIAL"
        self._active_flights = 0
        self._iss_lat_lon = "ISS: 0.00°N, 0.00°E"

    @property
    def title_text(self) -> str:
        return self._title_text

    @property
    def active_flights(self) -> int:
        return self._active_flights

    @property
    def iss_lat_lon(self) -> str:
        return self._iss_lat_lon

    def update_telemetry(self, flights: int, iss_pos: str) -> None:
        self._active_flights = flights
        self._iss_lat_lon = iss_pos
        self.data_changed.emit()
