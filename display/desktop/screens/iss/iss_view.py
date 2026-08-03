"""
AeroTracker Core — ISS View (MVC)
=================================
View pura do rastreador da ISS com telemetria orbital Glass Cockpit.
"""

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QGridLayout, QHBoxLayout, QLabel, QVBoxLayout, QWidget

from display.components.animated_card import GlassPanel
from display.components.primary_button import GlassButton
from display.components.status_badge import AvionicsBadge
from display.desktop.screens.iss.iss_model import ISSModel
from display.theme import Theme


class ISSView(QWidget):
    """
    View pura do módulo ISS.
    """

    refresh_requested = Signal()

    def __init__(self, model: ISSModel, parent=None) -> None:
        super().__init__(parent)
        self.model = model

        layout = QVBoxLayout(self)
        layout.setContentsMargins(Theme.Dimensions.PAD_L, Theme.Dimensions.PAD_L, Theme.Dimensions.PAD_L, Theme.Dimensions.PAD_L)
        layout.setSpacing(Theme.Dimensions.PAD_M)

        # Header Bar
        header = QHBoxLayout()
        self.lbl_title = QLabel(self.model.title_text)
        self.lbl_title.setFont(Theme.Fonts.title_display())
        self.lbl_title.setStyleSheet(f"color: {Theme.Colors.CYAN_NEON};")
        header.addWidget(self.lbl_title)
        header.addStretch()

        self.btn_refresh = GlassButton("🔄 TRACK ISS", is_primary=True)
        self.btn_refresh.clicked.connect(self.refresh_requested.emit)
        header.addWidget(self.btn_refresh)
        layout.addLayout(header)

        # Telemetry Instruments Grid
        grid = QGridLayout()
        grid.setSpacing(Theme.Dimensions.PAD_M)

        self.card_lat = self._create_metric_card("LATITUDE", self.model.lat_text)
        self.card_lon = self._create_metric_card("LONGITUDE", self.model.lon_text)
        self.card_alt = self._create_metric_card("ALTITUDE", self.model.alt_text)
        self.card_spd = self._create_metric_card("ORBITAL SPEED", self.model.spd_text)

        grid.addWidget(self.card_lat, 0, 0)
        grid.addWidget(self.card_lon, 0, 1)
        grid.addWidget(self.card_alt, 1, 0)
        grid.addWidget(self.card_spd, 1, 1)

        layout.addLayout(grid)

        # Visibility Badge Panel
        panel = GlassPanel()
        p_layout = QHBoxLayout(panel)
        p_layout.addWidget(QLabel("ORBITAL VISIBILITY STATE:"))
        self.badge_vis = AvionicsBadge(self.model.vis_text, badge_type="positive")
        p_layout.addWidget(self.badge_vis)
        p_layout.addStretch()

        layout.addWidget(panel)
        layout.addStretch()

        self.model.data_changed.connect(self.update_from_model)

    def _create_metric_card(self, title: str, val: str) -> GlassPanel:
        panel = GlassPanel()
        lbl_t = QLabel(title)
        lbl_t.setFont(Theme.Fonts.caption())
        lbl_t.setStyleSheet(f"color: {Theme.Colors.TEXT_MUTED}; border: none;")
        panel.main_layout.addWidget(lbl_t)

        lbl_v = QLabel(val)
        lbl_v.setFont(Theme.Fonts.metric_huge())
        lbl_v.setStyleSheet(f"color: {Theme.Colors.CYAN_NEON}; border: none;")
        panel.main_layout.addWidget(lbl_v)
        panel.lbl_val = lbl_v
        return panel

    def update_from_model(self) -> None:
        self.card_lat.lbl_val.setText(self.model.lat_text)
        self.card_lon.lbl_val.setText(self.model.lon_text)
        self.card_alt.lbl_val.setText(self.model.alt_text)
        self.card_spd.lbl_val.setText(self.model.spd_text)
