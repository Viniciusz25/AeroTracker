"""
AeroTracker Core — Clock View (MVC)
===================================
View pura de cronômetro e relógio de precisão aeroespacial Airspace Companion UI.
"""

from PySide6.QtWidgets import QGridLayout, QLabel, QVBoxLayout, QWidget
from display.components.animated_card import GlassPanel
from display.desktop.screens.clock.clock_model import ClockModel
from display.theme import Theme


class ClockView(QWidget):
    """
    View pura do módulo Clock.
    """

    def __init__(self, model: ClockModel, parent=None) -> None:
        super().__init__(parent)
        self.model = model

        layout = QVBoxLayout(self)
        layout.setContentsMargins(Theme.Dimensions.PAD_L, Theme.Dimensions.PAD_L, Theme.Dimensions.PAD_L, Theme.Dimensions.PAD_L)

        # Header
        self.lbl_title = QLabel(self.model.title_text)
        self.lbl_title.setFont(Theme.Fonts.title_display())
        self.lbl_title.setStyleSheet(f"color: {Theme.Colors.TEXT_PRIMARY};")
        layout.addWidget(self.lbl_title)

        grid = QGridLayout()
        grid.setSpacing(Theme.Dimensions.PAD_M)

        p1 = GlassPanel()
        lbl_p1 = QLabel("UNIVERSAL TIME COORDINATED (UTC)")
        lbl_p1.setFont(Theme.Fonts.caption())
        lbl_p1.setStyleSheet(f"color: {Theme.Colors.TEXT_MUTED}; border: none;")
        p1.main_layout.addWidget(lbl_p1)

        self.lbl_utc = QLabel(self.model.utc_time_str)
        self.lbl_utc.setFont(Theme.Fonts.metric_huge())
        self.lbl_utc.setStyleSheet(f"color: {Theme.Colors.PRIMARY}; border: none;")
        p1.main_layout.addWidget(self.lbl_utc)

        p2 = GlassPanel()
        lbl_p2 = QLabel("LOCAL STATION TIME")
        lbl_p2.setFont(Theme.Fonts.caption())
        lbl_p2.setStyleSheet(f"color: {Theme.Colors.TEXT_MUTED}; border: none;")
        p2.main_layout.addWidget(lbl_p2)

        self.lbl_local = QLabel(self.model.local_time_str)
        self.lbl_local.setFont(Theme.Fonts.metric_huge())
        self.lbl_local.setStyleSheet(f"color: {Theme.Colors.TEXT_PRIMARY}; border: none;")
        p2.main_layout.addWidget(self.lbl_local)

        grid.addWidget(p1, 0, 0)
        grid.addWidget(p2, 0, 1)

        layout.addLayout(grid)
        layout.addStretch()

        self.model.time_updated.connect(self.update_from_model)

    def update_from_model(self) -> None:
        self.lbl_utc.setText(self.model.utc_time_str)
        self.lbl_local.setText(self.model.local_time_str)
