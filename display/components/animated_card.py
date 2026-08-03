"""
AeroTracker Core — Componente AnimatedCard
==========================================
Card visual interativo com animações suaves de hover utilizando QPropertyAnimation.
"""

from PySide6.QtCore import QEasingCurve, QPropertyAnimation, QRect, Qt
from PySide6.QtWidgets import QFrame, QGraphicsOpacityEffect, QVBoxLayout

from display.theme import Theme


class AnimatedCard(QFrame):
    """
    Card reutilizável estilizado com animações dinâmicas de transição e opacidade via QPropertyAnimation.
    """

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("AnimatedCard")
        self.setStyleSheet(f"""
            QFrame#AnimatedCard {{
                background-color: {Theme.Colors.BG_CARD};
                border: 1px solid {Theme.Colors.BORDER};
                border-radius: {Theme.Dimensions.RADIUS_CARD}px;
            }}
        """)

        # Layout interno automático
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(
            Theme.Dimensions.PAD_M,
            Theme.Dimensions.PAD_M,
            Theme.Dimensions.PAD_M,
            Theme.Dimensions.PAD_M,
        )
        self.main_layout.setSpacing(Theme.Dimensions.PAD_S)

        # Efeito de opacidade para animação
        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.opacity_effect.setOpacity(0.92)
        self.setGraphicsEffect(self.opacity_effect)

        # Configuração da animação QPropertyAnimation
        self.anim_opacity = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.anim_opacity.setDuration(180)
        self.anim_opacity.setEasingCurve(QEasingCurve.Type.OutCubic)

    def enterEvent(self, event) -> None:
        """Dispara animação QPropertyAnimation ao passar o cursor."""
        self.setStyleSheet(f"""
            QFrame#AnimatedCard {{
                background-color: {Theme.Colors.BG_CARD_HOVER};
                border: 1px solid {Theme.Colors.PRIMARY};
                border-radius: {Theme.Dimensions.RADIUS_CARD}px;
            }}
        """)
        self.anim_opacity.stop()
        self.anim_opacity.setStartValue(self.opacity_effect.opacity())
        self.anim_opacity.setEndValue(1.0)
        self.anim_opacity.start()
        super().enterEvent(event)

    def leaveEvent(self, event) -> None:
        """Dispara animação QPropertyAnimation ao retirar o cursor."""
        self.setStyleSheet(f"""
            QFrame#AnimatedCard {{
                background-color: {Theme.Colors.BG_CARD};
                border: 1px solid {Theme.Colors.BORDER};
                border-radius: {Theme.Dimensions.RADIUS_CARD}px;
            }}
        """)
        self.anim_opacity.stop()
        self.anim_opacity.setStartValue(self.opacity_effect.opacity())
        self.anim_opacity.setEndValue(0.92)
        self.anim_opacity.start()
        super().leaveEvent(event)
