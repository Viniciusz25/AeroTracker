"""
AeroTracker Core — Settings View (MVC)
======================================
View pura de configurações do cockpit.
"""

from PySide6.QtWidgets import QHBoxLayout, QLabel, QVBoxLayout, QWidget
from display.components.animated_card import GlassPanel
from display.components.status_badge import AvionicsBadge
from display.desktop.screens.settings.settings_model import SettingsModel
from display.theme import Theme


class SettingsView(QWidget):
    """
    View pura do módulo Settings.
    """

    def __init__(self, model: SettingsModel, parent=None) -> None:
        super().__init__(parent)
        self.model = model

        layout = QVBoxLayout(self)
        layout.setContentsMargins(Theme.Dimensions.PAD_L, Theme.Dimensions.PAD_L, Theme.Dimensions.PAD_L, Theme.Dimensions.PAD_L)

        # Header
        self.lbl_title = QLabel(self.model.title_text)
        self.lbl_title.setFont(Theme.Fonts.title_display())
        self.lbl_title.setStyleSheet(f"color: {Theme.Colors.CYAN_NEON};")
        layout.addWidget(self.lbl_title)

        p1 = GlassPanel()
        top1 = QHBoxLayout()
        top1.addWidget(QLabel("UNITS SYSTEM:"))
        top1.addWidget(QLabel(self.model.units_text))
        top1.addStretch()
        p1.main_layout.addLayout(top1)

        p2 = GlassPanel()
        top2 = QHBoxLayout()
        top2.addWidget(QLabel("SUBSYSTEM HEALTH STATUS:"))
        top2.addWidget(AvionicsBadge("ALL ONLINE", badge_type="positive"))
        top2.addStretch()
        p2.main_layout.addLayout(top2)

        layout.addWidget(p1)
        layout.addWidget(p2)
        layout.addStretch()
