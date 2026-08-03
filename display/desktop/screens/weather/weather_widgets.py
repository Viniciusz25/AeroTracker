"""
AeroTracker Core — Weather Widgets
==================================
Widgets reutilizáveis específicos da tela de Clima.
"""

from PySide6.QtWidgets import QLabel
from display.components.animated_card import AnimatedCard
from display.theme import Theme


class WeatherMetricCardWidget(AnimatedCard):
    """
    Card estilizado para métrica meteorológica individual.
    """

    def __init__(self, title: str, initial_text: str, parent=None) -> None:
        super().__init__(parent)

        self.lbl_title = QLabel(title)
        self.lbl_title.setFont(Theme.Fonts.caption())
        self.lbl_title.setStyleSheet(f"color: {Theme.Colors.TEXT_SECONDARY}; border: none;")
        self.main_layout.addWidget(self.lbl_title)

        self.lbl_val = QLabel(initial_text)
        self.lbl_val.setFont(Theme.Fonts.card_title())
        self.lbl_val.setStyleSheet(f"color: {Theme.Colors.TEXT_PRIMARY}; border: none;")
        self.main_layout.addWidget(self.lbl_val)

    def set_value(self, text: str) -> None:
        self.lbl_val.setText(text)
