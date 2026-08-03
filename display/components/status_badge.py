"""
AeroTracker Core — Componente StatusBadge
========================================
Badge indicador de estado operacional reutilizável.
"""

from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel
from display.theme import Theme


class StatusBadge(QFrame):
    """
    Badge de status com cores e estilos padronizados pelo Theme.py.
    """

    def __init__(self, text: str, badge_type: str = "success", parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("StatusBadge")

        type_colors = {
            "success": (Theme.Colors.AIRBORNE, Theme.Colors.AIRBORNE_BG),
            "warning": (Theme.Colors.ON_GROUND, Theme.Colors.ON_GROUND_BG),
            "error": (Theme.Colors.ERROR, Theme.Colors.ERROR_BG),
            "info": (Theme.Colors.PRIMARY, "#0A2533"),
        }
        text_color, bg_color = type_colors.get(badge_type, type_colors["info"])

        self.setStyleSheet(f"""
            QFrame#StatusBadge {{
                background-color: {bg_color};
                border: 1px solid {text_color};
                border-radius: {Theme.Dimensions.RADIUS_BADGE}px;
            }}
            QLabel {{
                color: {text_color};
                font-weight: bold;
                font-size: 10px;
                border: none;
            }}
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(6, 2, 6, 2)
        self.lbl_text = QLabel(f"● {text.upper()}")
        layout.addWidget(self.lbl_text)
