"""
AeroTracker Core — Tracker Model (MVC)
======================================
Modelo de dados do módulo Tracker (Acompanhamento e agendamento de voos).
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

        # Voo Ativo
        self._active_flight = "YP113"
        self._departure_date = "8/1/2026"
        self._origin_code = "ICN"
        self._origin_city = "Seoul"
        self._dest_code = "SFO"
        self._dest_city = "San Francisco"
        self._aircraft_type = "Aircraft type unavailable"
        self._duration = "11h"
        self._distance = "9107 km"
        self._eta = "1:00 PM"
        self._progress_pct = 0

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
