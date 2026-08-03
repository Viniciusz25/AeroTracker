"""
AeroTracker Core — Aircraft Model (MVC)
=======================================
Modelo de dados e estado da tela de Radar de Aeronaves.
Todos os textos e listas derivam desta classe.
"""

from PySide6.QtCore import QObject, Signal
from models.aircraft import AircraftList, AircraftState


class AircraftModel(QObject):
    """
    Model do Radar de Aeronaves.
    Emite os sinais data_changed e status_changed para a View.
    """

    data_changed = Signal()
    status_changed = Signal(str)

    def __init__(self) -> None:
        super().__init__()
        self._title_text = "📡 Radar de Aeronaves (OpenSky Network)"
        self._aircraft_list: list[AircraftState] = []
        self._total_count = 0
        self._airborne_count = 0
        self._on_ground_count = 0
        self._status_text = "Aguardando primeira varredura do radar..."

    @property
    def title_text(self) -> str:
        return self._title_text

    @property
    def status_text(self) -> str:
        return self._status_text

    @property
    def aircraft_list(self) -> list[AircraftState]:
        return self._aircraft_list

    @property
    def summary_text(self) -> str:
        return f"Total: {self._total_count} aeronaves   |   ✈️ Em voo: {self._airborne_count}   |   🛬 Em solo: {self._on_ground_count}"

    def update_data(self, data: AircraftList | list[AircraftState]) -> None:
        """Atualiza os dados de aeronaves mantidos pelo Model."""
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

        self._status_text = self.summary_text
        self.data_changed.emit()

    def set_status_message(self, message: str) -> None:
        self._status_text = message
        self.status_changed.emit(message)
