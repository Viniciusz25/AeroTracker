"""
AeroTracker Core — Settings View (MVC)
======================================
View pura de configurações do cockpit Airspace Companion UI.
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
        self.lbl_title.setStyleSheet(f"color: {Theme.Colors.TEXT_PRIMARY};")
        layout.addWidget(self.lbl_title)

        p1 = GlassPanel()
        top1 = QHBoxLayout()
        lbl1 = QLabel("UNITS SYSTEM:")
        lbl1.setFont(Theme.Fonts.body_bold())
        lbl1.setStyleSheet(f"color: {Theme.Colors.TEXT_MUTED}; border: none;")
        top1.addWidget(lbl1)

        val1 = QLabel(self.model.units_text)
        val1.setFont(Theme.Fonts.body_bold())
        val1.setStyleSheet(f"color: {Theme.Colors.PRIMARY}; border: none;")
        top1.addWidget(val1)
        top1.addStretch()
        p1.main_layout.addLayout(top1)

        p2 = GlassPanel()
        top2 = QHBoxLayout()
        lbl2 = QLabel("SUBSYSTEM HEALTH STATUS:")
        lbl2.setFont(Theme.Fonts.body_bold())
        lbl2.setStyleSheet(f"color: {Theme.Colors.TEXT_MUTED}; border: none;")
        top2.addWidget(lbl2)

        top2.addWidget(AvionicsBadge("ALL ONLINE", badge_type="positive"))
        top2.addStretch()
        p2.main_layout.addLayout(top2)

        layout.addWidget(p1)
        layout.addWidget(p2)
        layout.addStretch()
