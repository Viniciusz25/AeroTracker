"""
AeroTracker Core — Aircraft Details View (MVC)
==============================================
View pura de inspeção detalhada de alvo aeroespacial.
"""

from PySide6.QtWidgets import QGridLayout, QLabel, QVBoxLayout, QWidget
from display.components.animated_card import GlassPanel
from display.components.status_badge import AvionicsBadge
from display.desktop.screens.aircraft_details.details_model import AircraftDetailsModel
from display.theme import Theme


class AircraftDetailsView(QWidget):
    """
    View pura do módulo Aircraft Details.
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

        grid = QGridLayout()
        grid.setSpacing(Theme.Dimensions.PAD_M)

        p1 = GlassPanel()
        p1.main_layout.addWidget(QLabel("CALLSIGN / IDENT"))
        self.lbl_cs = QLabel(self.model.callsign)
        self.lbl_cs.setFont(Theme.Fonts.metric_huge())
        self.lbl_cs.setStyleSheet(f"color: {Theme.Colors.CYAN_NEON}; border: none;")
        p1.main_layout.addWidget(self.lbl_cs)

        p2 = GlassPanel()
        p2.main_layout.addWidget(QLabel("ICAO24 TRANSPONDER"))
        self.lbl_icao = QLabel(self.model.icao24)
        self.lbl_icao.setFont(Theme.Fonts.metric_huge())
        self.lbl_icao.setStyleSheet(f"color: {Theme.Colors.TEXT_PRIMARY}; border: none;")
        p2.main_layout.addWidget(self.lbl_icao)

        p3 = GlassPanel()
        p3.main_layout.addWidget(QLabel("ALTITUDE (MSL)"))
        self.lbl_alt = QLabel(self.model.altitude)
        self.lbl_alt.setFont(Theme.Fonts.metric_huge())
        self.lbl_alt.setStyleSheet(f"color: {Theme.Colors.POSITIVE}; border: none;")
        p3.main_layout.addWidget(self.lbl_alt)

        p4 = GlassPanel()
        p4.main_layout.addWidget(QLabel("GROUND SPEED"))
        self.lbl_spd = QLabel(self.model.speed)
        self.lbl_spd.setFont(Theme.Fonts.metric_huge())
        self.lbl_spd.setStyleSheet(f"color: {Theme.Colors.BLUE_NEON}; border: none;")
        p4.main_layout.addWidget(self.lbl_spd)

        grid.addWidget(p1, 0, 0)
        grid.addWidget(p2, 0, 1)
        grid.addWidget(p3, 1, 0)
        grid.addWidget(p4, 1, 1)

        layout.addLayout(grid)
        layout.addStretch()

        self.model.data_changed.connect(self.update_from_model)

    def update_from_model(self) -> None:
        self.lbl_cs.setText(self.model.callsign)
        self.lbl_icao.setText(self.model.icao24)
        self.lbl_alt.setText(self.model.altitude)
        self.lbl_spd.setText(self.model.speed)
