"""
AeroTracker Core — Theme & Design System (PySide6 / Qt)
======================================================
Centraliza todas as cores, estilos QSS, fontes e tokens visuais da aplicação.
Toda cor e estilo visual do projeto devem derivar deste arquivo.
"""

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QFont


class Theme:
    """
    Design System central do AeroTracker (Qt / PySide6).
    """

    class Colors:
        """Paleta de cores padronizada (Dark Mode High-Tech)."""

        BG_DARK = "#0B0E14"
        BG_SIDEBAR = "#121722"
        BG_CARD = "#1A2130"
        BG_CARD_HOVER = "#232D42"
        BG_HEADER = "#161D2B"

        PRIMARY = "#00D2FF"
        PRIMARY_HOVER = "#00A3CC"
        SECONDARY = "#3A7BD5"
        SECONDARY_HOVER = "#2A5B9E"

        AIRBORNE = "#00E676"
        AIRBORNE_BG = "#0A291B"
        ON_GROUND = "#FFB300"
        ON_GROUND_BG = "#2E2408"
        ERROR = "#FF5252"
        ERROR_BG = "#331212"

        TEXT_PRIMARY = "#F0F4F8"
        TEXT_SECONDARY = "#94A3B8"
        TEXT_MUTED = "#64748B"

        BORDER = "#2A354B"
        BORDER_LIGHT = "#3B4A66"

        @classmethod
        def qcolor(cls, hex_code: str) -> QColor:
            """Retorna um objeto QColor a partir do código hexadecimal."""
            return QColor(hex_code)

    class Fonts:
        """Tokens de Tipografia."""

        FONT_FAMILY = "Segoe UI"

        @classmethod
        def title_main(cls) -> QFont:
            font = QFont(cls.FONT_FAMILY, 20)
            font.setBold(True)
            return font

        @classmethod
        def title_section(cls) -> QFont:
            font = QFont(cls.FONT_FAMILY, 16)
            font.setBold(True)
            return font

        @classmethod
        def card_title(cls) -> QFont:
            font = QFont(cls.FONT_FAMILY, 13)
            font.setBold(True)
            return font

        @classmethod
        def body(cls) -> QFont:
            return QFont(cls.FONT_FAMILY, 11)

        @classmethod
        def body_bold(cls) -> QFont:
            font = QFont(cls.FONT_FAMILY, 11)
            font.setBold(True)
            return font

        @classmethod
        def caption(cls) -> QFont:
            return QFont(cls.FONT_FAMILY, 9)

        @classmethod
        def metric_large(cls) -> QFont:
            font = QFont(cls.FONT_FAMILY, 26)
            font.setBold(True)
            return font

    class Dimensions:
        """Tokens de Espaçamento e Raios."""

        RADIUS_CARD = 12
        RADIUS_BUTTON = 8
        RADIUS_BADGE = 6

        PAD_XS = 4
        PAD_S = 8
        PAD_M = 16
        PAD_L = 24

    class Styles:
        """Estilos globais em formato QSS (Qt Style Sheets)."""

        @classmethod
        def app_stylesheet(cls) -> str:
            return f"""
                QMainWindow {{
                    background-color: {Theme.Colors.BG_DARK};
                }}
                QWidget {{
                    font-family: "{Theme.Fonts.FONT_FAMILY}";
                    color: {Theme.Colors.TEXT_PRIMARY};
                }}
                QScrollArea {{
                    border: none;
                    background-color: transparent;
                }}
                QScrollBar:vertical {{
                    border: none;
                    background: {Theme.Colors.BG_SIDEBAR};
                    width: 8px;
                    border-radius: 4px;
                }}
                QScrollBar::handle:vertical {{
                    background: {Theme.Colors.BORDER_LIGHT};
                    border-radius: 4px;
                    min-height: 20px;
                }}
                QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                    height: 0px;
                }}
            """
