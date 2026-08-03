"""
AeroTracker Core — Radar Model (MVC)
=====================================
Modelo de dados da tela de Radar ATC de Controle de Tráfego Aéreo.
"""

from PySide6.QtCore import QObject, Signal
from models.aircraft import AircraftList, AircraftState


class RadarModel(QObject):
    """
    Model da tela de Radar ATC.
    """

    data_changed = Signal()

    def __init__(self) -> None:
        super().__init__()
        self._title_text = "📡 RADAR ATC — CONTROLE DE TRÁFEGO AÉREO"
        self._aircraft_list: list[AircraftState] = []
        self._total_count = 0
        self._airborne_count = 0
        self._on_ground_count = 0

    @property
    def title_text(self) -> str:
        return self._title_text

    @property
    def aircraft_list(self) -> list[AircraftState]:
        return self._aircraft_list

    @property
    def status_summary(self) -> str:
        return f"CONTATO: {self._total_count} AIRBORNE: {self._airborne_count} GROUND: {self._on_ground_count}"

    def update_data(self, data: AircraftList | list[AircraftState]) -> None:
        if isinstance(data, AircraftList):
            self._aircraft_list = data.aircraft
            self._total_count = data.total_count
            self._airborne_count = data.airborne_count
            self._on_ground_count = data.on_ground_count
        elif isinstance(data, list):
            self._aircraft_list = data
            self._total_count = len(data)
            self._airborne_count = sum(1 for a in data if not getattr(a, "on_ground", False))
            self._on_ground_count = self._total_count - self._airborne_count

        self.data_changed.emit()
