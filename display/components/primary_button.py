"""
AeroTracker Core — Botões com QPropertyAnimation
================================================
Botões estilizados com animações suaves de transição via QPropertyAnimation.
"""

from PySide6.QtCore import QEasingCurve, QPropertyAnimation
from PySide6.QtWidgets import QGraphicsOpacityEffect, QPushButton
from display.theme import Theme


class AnimatedButton(QPushButton):
    """
    Botão interativo base com animação QPropertyAnimation de opacidade/destaque.
    """

    def __init__(self, text: str, is_primary: bool = True, parent=None) -> None:
        super().__init__(text, parent)
        self.is_primary = is_primary
        self._apply_style()

        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.opacity_effect.setOpacity(0.9)
        self.setGraphicsEffect(self.opacity_effect)

        self.anim = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.anim.setDuration(150)
        self.anim.setEasingCurve(QEasingCurve.Type.OutQuad)

    def _apply_style(self) -> None:
        if self.is_primary:
            self.setStyleSheet(f"""
                QPushButton {{
                    background-color: {Theme.Colors.PRIMARY};
                    color: #000000;
                    font-weight: bold;
                    font-size: 12px;
                    border: none;
                    border-radius: {Theme.Dimensions.RADIUS_BUTTON}px;
                    padding: 8px 16px;
                }}
                QPushButton:hover {{
                    background-color: {Theme.Colors.PRIMARY_HOVER};
                }}
            """)
        else:
            self.setStyleSheet(f"""
                QPushButton {{
                    background-color: {Theme.Colors.BG_CARD};
                    color: {Theme.Colors.TEXT_PRIMARY};
                    font-size: 12px;
                    border: 1px solid {Theme.Colors.BORDER_LIGHT};
                    border-radius: {Theme.Dimensions.RADIUS_BUTTON}px;
                    padding: 8px 16px;
                }}
                QPushButton:hover {{
                    background-color: {Theme.Colors.BG_CARD_HOVER};
                    border-color: {Theme.Colors.PRIMARY};
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
        self.anim.setEndValue(0.9)
        self.anim.start()
        super().leaveEvent(event)
