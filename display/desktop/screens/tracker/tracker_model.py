"""
AeroTracker Core — Tracker Model (MVC)
======================================
Modelo de dados do módulo Tracker (Acompanhamento e agendamento de voos em tempo real).
"""

from PySide6.QtCore import QObject, Signal


class TrackerModel(QObject):
    """
    Model de dados do módulo Tracker.
    """

    data_changed = Signal()

    def __init__(self) -> None:
        super().__init__()
        self._title_text = "Tracker"
        self._subtitle_text = "Scheduled family flights"

        # Voo Ativo e Rota
        self._active_flight = "YP113"
        self._departure_date = "8/1/2026"
        self._origin_code = "ICN"
        self._origin_city = "Seoul"
        self._dest_code = "SFO"
        self._dest_city = "San Francisco"
        self._aircraft_type = "Boeing 777-300ER"
        self._total_distance_km = 9107
        self._duration = "11h"
        self._distance = "9107 km"
        self._eta = "1:00 PM"

        # Telemetria em Tempo Real
        self._progress_pct = 15
        self._dist_from_km = 1366
        self._dist_to_km = 7741
        self._status_str = "EN ROUTE · 15%"

    @property
    def title_text(self) -> str:
        return self._title_text

    @property
    def subtitle_text(self) -> str:
        return self._subtitle_text

    @property
    def active_flight(self) -> str:
        return self._active_flight

    @property
    def departure_date(self) -> str:
        return self._departure_date

    @property
    def origin_code(self) -> str:
        return self._origin_code

    @property
    def origin_city(self) -> str:
        return self._origin_city

    @property
    def dest_code(self) -> str:
        return self._dest_code

    @property
    def dest_city(self) -> str:
        return self._dest_city

    @property
    def aircraft_type(self) -> str:
        return self._aircraft_type

    @property
    def duration(self) -> str:
        return self._duration

    @property
    def distance(self) -> str:
        return self._distance

    @property
    def eta(self) -> str:
        return self._eta

    @property
    def progress_pct(self) -> int:
        return self._progress_pct

    @property
    def dist_from_str(self) -> str:
        return f"{self._dist_from_km} km"

    @property
    def dist_to_str(self) -> str:
        return f"{self._dist_to_km} km"

    @property
    def status_str(self) -> str:
        return self._status_str

    def set_active_flight(self, flight_number: str, departure_date: str = "") -> None:
        """Atualiza o número do voo ativo e reinicia a telemetria."""
        if flight_number:
            self._active_flight = flight_number.strip().upper()
        if departure_date:
            self._departure_date = departure_date.strip()
        self._progress_pct = 0
        self._dist_from_km = 0
        self._dist_to_km = self._total_distance_km
        self._status_str = "TAXI / DEPARTING"
        self.data_changed.emit()

    def update_telemetry(self, progress_pct: int, dist_from_km: int, dist_to_km: int, status_str: str = "") -> None:
        """Atualiza telemetria em tempo real."""
        self._progress_pct = max(0, min(100, progress_pct))
        self._dist_from_km = dist_from_km
        self._dist_to_km = dist_to_km
        if status_str:
            self._status_str = status_str
        else:
            self._status_str = f"EN ROUTE · {self._progress_pct}%"
        self.data_changed.emit()
