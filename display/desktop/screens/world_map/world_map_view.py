"""
AeroTracker Core — WorldMap View (MVC)
======================================
View do Mapa Mundial Global com renderização de projection grid estilo Glass Cockpit.
"""

from PySide6.QtWidgets import QHBoxLayout, QLabel, QVBoxLayout, QWidget
from display.components.animated_card import GlassPanel
from display.components.status_badge import AvionicsBadge
from display.desktop.screens.world_map.world_map_model import WorldMapModel
from display.theme import Theme


class WorldMapView(QWidget):
    """
    View pura do Mapa Mundial Global.
    """

    def __init__(self, model: WorldMapModel, parent=None) -> None:
        super().__init__(parent)
        self.model = model

        layout = QVBoxLayout(self)
        layout.setContentsMargins(Theme.Dimensions.PAD_L, Theme.Dimensions.PAD_L, Theme.Dimensions.PAD_L, Theme.Dimensions.PAD_L)

        # Header
        self.lbl_title = QLabel(self.model.title_text)
        self.lbl_title.setFont(Theme.Fonts.title_display())
        self.lbl_title.setStyleSheet(f"color: {Theme.Colors.CYAN_NEON};")
        layout.addWidget(self.lbl_title)

        # Main Globe Instrument Panel
        panel = GlassPanel()
        p_layout = QVBoxLayout(panel)

        top_info = QHBoxLayout()
        self.lbl_flights = QLabel(f"GLOBAL FLIGHT TRACKS: {self.model.active_flights}")
        self.lbl_flights.setFont(Theme.Fonts.metric_huge())
        self.lbl_flights.setStyleSheet(f"color: {Theme.Colors.BLUE_NEON}; border: none;")
        top_info.addWidget(self.lbl_flights)
        top_info.addStretch()
        top_info.addWidget(AvionicsBadge("GLOBAL PROJECTION ACTIVE", badge_type="positive"))
        p_layout.addLayout(top_info)

        self.lbl_iss = QLabel(self.model.iss_lat_lon)
        self.lbl_iss.setFont(Theme.Fonts.body_bold())
        self.lbl_iss.setStyleSheet(f"color: {Theme.Colors.CYAN_NEON}; border: none;")
        p_layout.addWidget(self.lbl_iss)

        layout.addWidget(panel)
        layout.addStretch()

        self.model.data_changed.connect(self.update_from_model)

    def update_from_model(self) -> None:
        self.lbl_flights.setText(f"GLOBAL FLIGHT TRACKS: {self.model.active_flights}")
        self.lbl_iss.setText(self.model.iss_lat_lon)
