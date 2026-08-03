"""
AeroTracker Core — Aircraft Details Model (MVC)
==============================================
Modelo de dados para inspeção detalhada de uma aeronave selecionada.
"""

from PySide6.QtCore import QObject, Signal


class AircraftDetailsModel(QObject):
    """
    Model da tela de Detalhes da Aeronave.
    """

    data_changed = Signal()

    def __init__(self) -> None:
        super().__init__()
        self._title_text = "🎯 TARGET INSPECTION — DETALHES DE NAVEGAÇÃO"
        self._callsign = "TAM3045"
        self._icao24 = "E48B2F"
        self._country = "Brazil"
        self._altitude = "10,668 m (FL350)"
        self._speed = "840 km/h (453 kts)"
        self._heading = "245° (WSW)"
        self._squawk = "7700"

    @property
    def title_text(self) -> str:
        return self._title_text

    @property
    def callsign(self) -> str:
        return self._callsign

    @property
    def icao24(self) -> str:
        return self._icao24

    @property
    def country(self) -> str:
        return self._country

    @property
    def altitude(self) -> str:
        return self._altitude

    @property
    def speed(self) -> str:
        return self._speed

    @property
    def heading(self) -> str:
        return self._heading

    @property
    def squawk(self) -> str:
        return self._squawk

    def select_aircraft(self, callsign: str, icao: str, country: str, alt: str, spd: str, hdg: str) -> None:
        self._callsign = callsign
        self._icao24 = icao
        self._country = country
        self._altitude = alt
        self._speed = spd
        self._heading = hdg
        self.data_changed.emit()
