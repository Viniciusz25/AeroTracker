"""
AeroTracker Core — Radar View (MVC)
===================================
View pura do Radar ATC com mapa vetorial e painel lateral de pistas.
"""

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QHBoxLayout, QLabel, QScrollArea, QVBoxLayout, QWidget

from display.components.animated_card import GlassPanel
from display.components.primary_button import GlassButton
from display.components.status_badge import AvionicsBadge
from display.components.vector_map_widget import VectorRadarWidget
from display.desktop.screens.radar.radar_model import RadarModel
from display.theme import Theme


class RadarView(QWidget):
    """
    View pura da tela de Radar ATC aeroespacial.
    """

    refresh_requested = Signal()

    def __init__(self, model: RadarModel, parent=None) -> None:
        super().__init__(parent)
        self.model = model

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(
            Theme.Dimensions.PAD_L,
            Theme.Dimensions.PAD_L,
            Theme.Dimensions.PAD_L,
            Theme.Dimensions.PAD_L,
        )
        self.main_layout.setSpacing(Theme.Dimensions.PAD_M)

        # Header Bar
        header_layout = QHBoxLayout()
        self.lbl_title = QLabel(self.model.title_text)
        self.lbl_title.setFont(Theme.Fonts.title_display())
        self.lbl_title.setStyleSheet(f"color: {Theme.Colors.CYAN_NEON};")
        header_layout.addWidget(self.lbl_title)
        header_layout.addStretch()

        self.btn_refresh = GlassButton("🔄 SCAN NOW", is_primary=True)
        self.btn_refresh.clicked.connect(self.refresh_requested.emit)
        header_layout.addWidget(self.btn_refresh)
        self.main_layout.addLayout(header_layout)

        # Status Summary Label
        self.lbl_status = QLabel(self.model.status_summary)
        self.lbl_status.setFont(Theme.Fonts.caption())
        self.lbl_status.setStyleSheet(f"color: {Theme.Colors.TEXT_SECONDARY};")
        self.main_layout.addWidget(self.lbl_status)

        # Split Content (Radar Vetorial à esquerda, Lista à direita)
        content_layout = QHBoxLayout()
        content_layout.setSpacing(Theme.Dimensions.PAD_M)

        self.vector_map = VectorRadarWidget(radius_km=250.0)
        self.vector_map.setMinimumSize(420, 420)
        content_layout.addWidget(self.vector_map, stretch=1)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_layout.setContentsMargins(0, 0, 0, 0)
        self.scroll_layout.setSpacing(Theme.Dimensions.PAD_S)
        self.scroll_layout.addStretch()
        self.scroll_area.setWidget(self.scroll_content)

        content_layout.addWidget(self.scroll_area, stretch=1)
        self.main_layout.addLayout(content_layout)

        self.model.data_changed.connect(self.update_from_model)

    def update_from_model(self) -> None:
        self.lbl_status.setText(self.model.status_summary)

        for i in reversed(range(self.scroll_layout.count() - 1)):
            item = self.scroll_layout.itemAt(i)
            if item and item.widget():
                item.widget().deleteLater()

        aircraft_list = self.model.aircraft_list
        for ac in aircraft_list:
            card = GlassPanel()
            top = QHBoxLayout()
            top.addWidget(QLabel(f"✈ {ac.display_id}"))
            badge_type = "attention" if ac.on_ground else "positive"
            top.addWidget(AvionicsBadge("GROUND" if ac.on_ground else "AIRBORNE", badge_type=badge_type))
            card.main_layout.addLayout(top)

            alt = f"{ac.altitude_m:,.0f}m" if ac.altitude_m is not None else "N/A"
            spd = f"{ac.speed_kmh:,.0f}km/h" if ac.speed_kmh is not None else "N/A"
            hdg = f"{ac.heading:.0f}°" if ac.heading is not None else "N/A"
            lbl = QLabel(f"ALT: {alt}  |  SPD: {spd}  |  HDG: {hdg}")
            lbl.setFont(Theme.Fonts.caption())
            card.main_layout.addWidget(lbl)
            self.scroll_layout.insertWidget(self.scroll_layout.count() - 1, card)

        self.vector_map.update_aircraft_markers(aircraft_list)
