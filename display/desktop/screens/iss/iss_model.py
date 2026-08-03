"""
AeroTracker Core — ISS Model (MVC)
==================================
Modelo de dados do rastreador da Estação Espacial Internacional (ISS).
"""

from PySide6.QtCore import QObject, Signal
from models.space import ISSPosition


class ISSModel(QObject):
    """
    Model da tela ISS.
    """

    data_changed = Signal()

    def __init__(self) -> None:
        super().__init__()
        self._title_text = "🛰 ISS TRACKER — ESTAÇÃO ESPACIAL INTERNACIONAL"
        self._lat_text = "--.----°"
        self._lon_text = "--.----°"
        self._alt_text = "408.0 km"
        self._spd_text = "27,600 km/h"
        self._vis_text = "DAYLIGHT"

    @property
    def title_text(self) -> str:
        return self._title_text

    @property
    def lat_text(self) -> str:
        return self._lat_text

    @property
    def lon_text(self) -> str:
        return self._lon_text

    @property
    def alt_text(self) -> str:
        return self._alt_text

    @property
    def spd_text(self) -> str:
        return self._spd_text

    @property
    def vis_text(self) -> str:
        return self._vis_text

    def update_position(self, pos: ISSPosition | dict) -> None:
        if isinstance(pos, ISSPosition):
            self._lat_text = f"{pos.position.latitude:.4f}°"
            self._lon_text = f"{pos.position.longitude:.4f}°"
            self._alt_text = f"{pos.altitude_km:.1f} km"
            self._spd_text = f"{pos.velocity_kmh:,.0f} km/h"
            self._vis_text = pos.visibility.upper() if pos.visibility else "ORBITAL"
        elif isinstance(pos, dict):
            self._lat_text = f"{pos.get('latitude', 0):.4f}°"
            self._lon_text = f"{pos.get('longitude', 0):.4f}°"
            self._alt_text = f"{pos.get('altitude', 408):.1f} km"
            self._spd_text = f"{pos.get('velocity', 27600):,.0f} km/h"
            self._vis_text = pos.get("visibility", "DAYLIGHT").upper()

        self.data_changed.emit()
