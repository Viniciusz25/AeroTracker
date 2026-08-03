"""
AeroTracker Core — Moon View (MVC)
==================================
View pura da tela de Efemérides Lunares.
"""

from PySide6.QtWidgets import QGridLayout, QLabel, QVBoxLayout, QWidget
from display.components.animated_card import GlassPanel
from display.desktop.screens.moon.moon_model import MoonModel
from display.theme import Theme


class MoonView(QWidget):
    """
    View pura do módulo Lunar.
    """

    def __init__(self, model: MoonModel, parent=None) -> None:
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
        p1.main_layout.addWidget(QLabel("LUNAR PHASE"))
        l1 = QLabel(self.model.phase_name)
        l1.setFont(Theme.Fonts.metric_huge())
        l1.setStyleSheet(f"color: {Theme.Colors.TEXT_PRIMARY}; border: none;")
        p1.main_layout.addWidget(l1)

        p2 = GlassPanel()
        p2.main_layout.addWidget(QLabel("ILLUMINATION"))
        l2 = QLabel(self.model.illumination)
        l2.setFont(Theme.Fonts.metric_huge())
        l2.setStyleSheet(f"color: {Theme.Colors.POSITIVE}; border: none;")
        p2.main_layout.addWidget(l2)

        p3 = GlassPanel()
        p3.main_layout.addWidget(QLabel("DISTANCE TO EARTH"))
        l3 = QLabel(self.model.distance_km)
        l3.setFont(Theme.Fonts.metric_huge())
        l3.setStyleSheet(f"color: {Theme.Colors.BLUE_NEON}; border: none;")
        p3.main_layout.addWidget(l3)

        grid.addWidget(p1, 0, 0)
        grid.addWidget(p2, 0, 1)
        grid.addWidget(p3, 1, 0, 1, 2)

        layout.addLayout(grid)
        layout.addStretch()
