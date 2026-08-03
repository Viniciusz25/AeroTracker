"""
AeroTracker Core — Botões Táticos Glass Cockpit
================================================
Botões de instrumentos aeroespaciais com animação QPropertyAnimation de resposta tátil.
"""

from PySide6.QtCore import QEasingCurve, QPropertyAnimation
from PySide6.QtWidgets import QGraphicsOpacityEffect, QPushButton
from display.theme import Theme


class GlassButton(QPushButton):
    """
    Botão tático minimalista para cockpits de aviação.
    """

    def __init__(self, text: str, is_primary: bool = True, parent=None) -> None:
        super().__init__(text, parent)
        self.is_primary = is_primary
        self._apply_style()

        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.opacity_effect.setOpacity(0.92)
        self.setGraphicsEffect(self.opacity_effect)

        self.anim = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.anim.setDuration(120)
        self.anim.setEasingCurve(QEasingCurve.Type.OutQuad)

    def _apply_style(self) -> None:
        if self.is_primary:
            self.setStyleSheet(f"""
                QPushButton {{
                    background-color: {Theme.Colors.BLUE_NEON};
                    color: {Theme.Colors.TEXT_PRIMARY};
                    font-family: "{Theme.Fonts.FONT_MONO}";
                    font-weight: bold;
                    font-size: 11px;
                    border: 1px solid {Theme.Colors.CYAN_NEON};
                    border-radius: {Theme.Dimensions.RADIUS_PANEL}px;
                    padding: 6px 14px;
                }}
                QPushButton:hover {{
                    background-color: {Theme.Colors.CYAN_NEON};
                    color: #000000;
                }}
            """)
        else:
            self.setStyleSheet(f"""
                QPushButton {{
                    background-color: {Theme.Colors.BG_PANEL};
                    color: {Theme.Colors.TEXT_PRIMARY};
                    font-family: "{Theme.Fonts.FONT_FAMILY}";
                    font-size: 11px;
                    border: 1px solid {Theme.Colors.BORDER};
                    border-radius: {Theme.Dimensions.RADIUS_PANEL}px;
                    padding: 6px 14px;
                }}
                QPushButton:hover {{
                    background-color: {Theme.Colors.BG_CARD_HOVER};
                    border-color: {Theme.Colors.CYAN_NEON};
                    color: {Theme.Colors.CYAN_NEON};
                }}
            """)

    def enterEvent(self, event) -> None:
        self.anim.stop()
        self.anim.setStartValue(self.opacity_effect.opacity())
        self.anim.setEndValue(1.0)
        self.anim.start()
        super().enterEvent(event)

    def leaveEvent(self, event) -> None:
        self.anim.stop()
        self.anim.setStartValue(self.opacity_effect.opacity())
        self.anim.setEndValue(0.92)
        self.anim.start()
        super().leaveEvent(event)


# Alias de compatibilidade
AnimatedButton = GlassButton
