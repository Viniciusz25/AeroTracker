"""
AeroTracker Core — SolarSystem View (MVC)
=========================================
View pura da tela de Efemérides do Sistema Solar.
"""

from PySide6.QtWidgets import QGridLayout, QLabel, QVBoxLayout, QWidget
from display.components.animated_card import GlassPanel
from display.desktop.screens.solar_system.solar_system_model import SolarSystemModel
from display.theme import Theme


class SolarSystemView(QWidget):
    """
    View pura do módulo Solar System.
    """

    def __init__(self, model: SolarSystemModel, parent=None) -> None:
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

        for idx, (name, dist, period) in enumerate(self.model.bodies):
            panel = GlassPanel()
            l_name = QLabel(f"🪐 {name.upper()}")
            l_name.setFont(Theme.Fonts.section_header())
            l_name.setStyleSheet(f"color: {Theme.Colors.CYAN_NEON}; border: none;")
            panel.main_layout.addWidget(l_name)

            l_dist = QLabel(f"Distance: {dist}  |  {period}")
            l_dist.setFont(Theme.Fonts.caption())
            l_dist.setStyleSheet(f"color: {Theme.Colors.TEXT_SECONDARY}; border: none;")
            panel.main_layout.addWidget(l_dist)

            row = idx // 2
            col = idx % 2
            grid.addWidget(panel, row, col)

        layout.addLayout(grid)
        layout.addStretch()
