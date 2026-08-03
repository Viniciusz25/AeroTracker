"""
AeroTracker Core — Componente AvionicsBadge
===========================================
Badge indicador de status aeroespacial com código de cores semântico estrito.
"""

from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel
from display.theme import Theme


class AvionicsBadge(QFrame):
    """
    Badge de status semântico estrito para cockpit.
    """

    def __init__(self, text: str, badge_type: str = "positive", parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("AvionicsBadge")

        # Regra: Verde apenas para informações positivas, Laranja para atenção, Vermelho para alertas.
        type_colors = {
            "positive": (Theme.Colors.POSITIVE, Theme.Colors.POSITIVE_BG),
            "attention": (Theme.Colors.ATTENTION, Theme.Colors.ATTENTION_BG),
            "alert": (Theme.Colors.ALERT, Theme.Colors.ALERT_BG),
            "neutral": (Theme.Colors.CYAN_NEON, "#061826"),
        }
        text_color, bg_color = type_colors.get(badge_type, type_colors["neutral"])

        self.setStyleSheet(f"""
            QFrame#AvionicsBadge {{
                background-color: {bg_color};
                border: 1px solid {text_color};
                border-radius: {Theme.Dimensions.RADIUS_BADGE}px;
            }}
            QLabel {{
                color: {text_color};
                font-family: "{Theme.Fonts.FONT_MONO}";
                font-weight: bold;
                font-size: 9px;
                border: none;
            }}
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(6, 2, 6, 2)
        self.lbl_text = QLabel(f"● {text.upper()}")
        layout.addWidget(self.lbl_text)


# Alias de compatibilidade
StatusBadge = AvionicsBadge
