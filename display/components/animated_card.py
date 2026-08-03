"""
AeroTracker Core — Componente GlassPanel
========================================
Moldura visual estilo painel Glass Cockpit / instrumento aeroespacial.
"""

from PySide6.QtWidgets import QFrame, QVBoxLayout
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
            QFrame#GlassPanel:hover {{
                background-color: {Theme.Colors.BG_CARD_HOVER};
                border: 1px solid {Theme.Colors.PRIMARY};
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


AnimatedCard = GlassPanel
