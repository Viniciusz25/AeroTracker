"""
AeroTracker Core — Aircraft Details View (MVC)
==============================================
View pura de inspeção detalhada de alvo aeroespacial com mostrador circular tático.
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QHBoxLayout, QLabel, QVBoxLayout, QWidget
from display.components.flight_tracker_gauge import FlightTrackerGauge
from display.desktop.screens.aircraft_details.details_model import AircraftDetailsModel
from display.theme import Theme


class AircraftDetailsView(QWidget):
    """
    View pura do módulo Target Inspection com mostrador circular de voo.
    """

    def __init__(self, model: AircraftDetailsModel, parent=None) -> None:
        super().__init__(parent)
        self.model = model

        layout = QVBoxLayout(self)
        layout.setContentsMargins(Theme.Dimensions.PAD_L, Theme.Dimensions.PAD_L, Theme.Dimensions.PAD_L, Theme.Dimensions.PAD_L)

        # Header
        self.lbl_title = QLabel(self.model.title_text)
        self.lbl_title.setFont(Theme.Fonts.title_display())
        self.lbl_title.setStyleSheet(f"color: {Theme.Colors.CYAN_NEON};")
        layout.addWidget(self.lbl_title)

        # Container Centralizado com o Mostrador Circular de Voo
        center_row = QHBoxLayout()
        center_row.addStretch()

        self.gauge = FlightTrackerGauge(self)
        self.gauge.update_flight_data(
            callsign="DL3073",
            aircraft_type="Airbus A319 114",
            origin_code="LAX",
            origin_city="Los Angeles",
            dest_code="SJC",
            dest_city="San Jose",
            altitude_str="15 m",
            speed_str="217 km/h",
            heading_str="NNW",
            progress=0.78,
        )

        center_row.addWidget(self.gauge)
        center_row.addStretch()

        layout.addLayout(center_row)
        layout.addStretch()

        self.model.data_changed.connect(self.update_from_model)

    def update_from_model(self) -> None:
        self.gauge.update_flight_data(
            callsign=self.model.callsign,
            aircraft_type="Airbus A319 114",
            origin_code="LAX",
            origin_city="Los Angeles",
            dest_code="SJC",
            dest_city="San Jose",
            altitude_str=self.model.altitude,
            speed_str=self.model.speed,
            heading_str=self.model.heading,
            progress=0.78,
        )
