"""
AeroTracker Core — Componente GlassPanel
========================================
Moldura visual estilo painel Glass Cockpit / instrumento aeroespacial.
"""

from PySide6.QtCore import QEasingCurve, QPropertyAnimation
from PySide6.QtWidgets import QFrame, QGraphicsOpacityEffect, QVBoxLayout
from display.theme import Theme


class GlassPanel(QFrame):
    """
    Painel de instrumento aeroespacial reutilizável com transparência e bordas técnicas.
    """

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("GlassPanel")
        self.setStyleSheet(f"""
            QFrame#GlassPanel {{
                background-color: {Theme.Colors.BG_CARD};
                border: 1px solid {Theme.Colors.BORDER};
                border-radius: {Theme.Dimensions.RADIUS_PANEL}px;
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

        # Transição de opacidade sutil via QPropertyAnimation
        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.opacity_effect.setOpacity(0.95)
        self.setGraphicsEffect(self.opacity_effect)

        self.anim_opacity = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.anim_opacity.setDuration(160)
        self.anim_opacity.setEasingCurve(QEasingCurve.Type.OutQuad)

    def enterEvent(self, event) -> None:
        """Sutil destaque de borda ao passar o cursor."""
        self.setStyleSheet(f"""
            QFrame#GlassPanel {{
                background-color: {Theme.Colors.BG_CARD_HOVER};
                border: 1px solid {Theme.Colors.CYAN_NEON};
                border-radius: {Theme.Dimensions.RADIUS_PANEL}px;
            }}
        """)
        self.anim_opacity.stop()
        self.anim_opacity.setStartValue(self.opacity_effect.opacity())
        self.anim_opacity.setEndValue(1.0)
        self.anim_opacity.start()
        super().enterEvent(event)

    def leaveEvent(self, event) -> None:
        """Restaura estilo padrão."""
        self.setStyleSheet(f"""
            QFrame#GlassPanel {{
                background-color: {Theme.Colors.BG_CARD};
                border: 1px solid {Theme.Colors.BORDER};
                border-radius: {Theme.Dimensions.RADIUS_PANEL}px;
            }}
        """)
        self.anim_opacity.stop()
        self.anim_opacity.setStartValue(self.opacity_effect.opacity())
        self.anim_opacity.setEndValue(0.95)
        self.anim_opacity.start()
        super().leaveEvent(event)


# Alias de compatibilidade
AnimatedCard = GlassPanel
