"""
AeroTracker Core — Launches View (MVC)
======================================
View pura de agenda de lançamentos espaciais Airspace Companion UI.
"""

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QHBoxLayout, QLabel, QScrollArea, QVBoxLayout, QWidget
from display.components.animated_card import GlassPanel
from display.components.primary_button import GlassButton
from display.components.status_badge import AvionicsBadge
from display.desktop.screens.launches.launches_model import LaunchesModel
from display.theme import Theme


class LaunchesView(QWidget):
    """
    View pura do módulo de Lançamentos Espaciais.
    """

    refresh_requested = Signal()

    def __init__(self, model: LaunchesModel, parent=None) -> None:
        super().__init__(parent)
        self.model = model

        layout = QVBoxLayout(self)
        layout.setContentsMargins(Theme.Dimensions.PAD_L, Theme.Dimensions.PAD_L, Theme.Dimensions.PAD_L, Theme.Dimensions.PAD_L)
        layout.setSpacing(Theme.Dimensions.PAD_M)

        # Header
        header = QHBoxLayout()
        self.lbl_title = QLabel(self.model.title_text)
        self.lbl_title.setFont(Theme.Fonts.title_display())
        self.lbl_title.setStyleSheet(f"color: {Theme.Colors.TEXT_PRIMARY};")
        header.addWidget(self.lbl_title)
        header.addStretch()

        self.btn_refresh = GlassButton("🔄 REFRESH SCHEDULE", is_primary=True)
        self.btn_refresh.clicked.connect(self.refresh_requested.emit)
        header.addWidget(self.btn_refresh)
        layout.addLayout(header)

        # List area
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_layout.setContentsMargins(0, 0, 0, 0)
        self.scroll_layout.setSpacing(Theme.Dimensions.PAD_S)
        self.scroll_layout.addStretch()
        self.scroll.setWidget(self.scroll_content)

        layout.addWidget(self.scroll)

        self.model.data_changed.connect(self.update_from_model)

    def update_from_model(self) -> None:
        for i in reversed(range(self.scroll_layout.count() - 1)):
            item = self.scroll_layout.itemAt(i)
            if item and item.widget():
                item.widget().deleteLater()

        for launch in self.model.launches:
            panel = GlassPanel()
            top = QHBoxLayout()
            l_name = QLabel(f"🚀 {launch.name}")
            l_name.setFont(Theme.Fonts.section_header())
            l_name.setStyleSheet(f"color: {Theme.Colors.TEXT_PRIMARY}; border: none;")
            top.addWidget(l_name)
            top.addStretch()

            st_name = launch.status.name if hasattr(launch.status, "name") else str(launch.status)
            top.addWidget(AvionicsBadge(st_name, badge_type="positive" if "GO" in st_name or "SUCCESS" in st_name else "attention"))
            panel.main_layout.addLayout(top)

            provider = launch.provider.name if launch.provider else "Agency Unknown"
            pad = launch.pad.name if launch.pad else "Pad Unknown"
            info = QLabel(f"PROVIDER: {provider}  |  PAD: {pad}")
            info.setFont(Theme.Fonts.caption())
            info.setStyleSheet(f"color: {Theme.Colors.TEXT_SECONDARY}; border: none;")
            panel.main_layout.addWidget(info)

            self.scroll_layout.insertWidget(self.scroll_layout.count() - 1, panel)
