"""
AeroTracker Core — Dashboard Widgets
====================================
Componentes visuais específicos do Dashboard construídos com AnimatedCard e layouts.
"""

from PySide6.QtWidgets import QLabel
from display.components.animated_card import AnimatedCard
from display.theme import Theme


class MetricCardWidget(AnimatedCard):
    """
    Card estilizado para métricas do Dashboard.
    """

    def __init__(self, title: str, initial_text: str, accent_color: str = Theme.Colors.PRIMARY, parent=None) -> None:
        super().__init__(parent)

        self.lbl_title = QLabel(title)
        self.lbl_title.setFont(Theme.Fonts.card_title())
        self.lbl_title.setStyleSheet(f"color: {Theme.Colors.TEXT_PRIMARY}; border: none;")
        self.main_layout.addWidget(self.lbl_title)

        self.lbl_value = QLabel(initial_text)
        self.lbl_value.setFont(Theme.Fonts.title_section())
        self.lbl_value.setStyleSheet(f"color: {accent_color}; border: none;")
        self.main_layout.addWidget(self.lbl_value)

    def set_value(self, text: str, color: str = None) -> None:
        self.lbl_value.setText(text)
        if color:
            self.lbl_value.setStyleSheet(f"color: {color}; border: none;")
