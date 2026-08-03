"""
AeroTracker Core — Airspace Companion & Avionics Design System
===============================================================
Estilo visual inspirado em Airspace Companion, Glass Cockpit e Mission Control.
"""

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QFont


class Theme:
    """
    Tokens visuais centralizados do Design System AeroTracker Core.
    """

    class Colors:
        """Paleta de cores tática oficial Airspace Companion."""

        # Planos de Fundo
        BG_DARK = "#050608"          # Preto profundo
        BG_SIDEBAR = "#080A0E"       # Sidebar lateral
        BG_PANEL = "#101214"         # Painéis secundários
        BG_CARD = "#14171C"          # Fundo de cartões
        BG_CARD_HOVER = "#1A1E25"    # Highlight sutil
        BG_INPUT = "#0B0E12"         # Fundo de entradas de texto

        # Acentos de Marca
        PRIMARY = "#47F3A0"         # Verde Menta Vibrante
        SECONDARY = "#33A8FF"       # Azul Aeroespacial
        CYAN_NEON = "#47F3A0"       # Alias primário
        BLUE_NEON = "#33A8FF"       # Alias secundário
        BORDER = "#20252B"          # Bordas sutis
        BORDER_HIGHLIGHT = "#47F3A0" # Borda ativa/selecionada

        # Status Semânticos
        POSITIVE = "#47F3A0"        # Verde (Em voo, OK, Ativo)
        POSITIVE_BG = "#0E2618"
        ATTENTION = "#FFC857"       # Âmbar (Atenção, Solo, Standby)
        ATTENTION_BG = "#261E0A"
        ALERT = "#FF5D5D"           # Vermelho (Emergência, Alerta)
        ALERT_BG = "#290A0A"

        # Aliases de compatibilidade
        AIRBORNE = POSITIVE
        ON_GROUND = ATTENTION
        ERROR = ALERT

        # Tipografia
        WHITE = "#FFFFFF"
        SUBTITLE = "#9BA4B0"
        TEXT_PRIMARY = "#FFFFFF"     # Branco puro
        TEXT_SECONDARY = "#9BA4B0"   # Subtítulos e dados secundários
        TEXT_MUTED = "#5A6472"       # Legendas discretas

        @classmethod
        def qcolor(cls, hex_code: str) -> QColor:
            return QColor(hex_code)

    class Fonts:
        """Tipografia moderna e limpa com hierarquia clara."""

        FONT_FAMILY = "Segoe UI"
        FONT_MONO = "Consolas"

        @classmethod
        def title_display(cls) -> QFont:
            return QFont(cls.FONT_FAMILY, 18, QFont.Weight.Bold)

        @classmethod
        def title_main(cls) -> QFont:
            return cls.title_display()

        @classmethod
        def title_section(cls) -> QFont:
            return QFont(cls.FONT_FAMILY, 13, QFont.Weight.Bold)

        @classmethod
        def section_header(cls) -> QFont:
            return cls.title_section()

        @classmethod
        def card_title(cls) -> QFont:
            return QFont(cls.FONT_FAMILY, 11, QFont.Weight.Bold)

        @classmethod
        def metric_huge(cls) -> QFont:
            return QFont(cls.FONT_FAMILY, 24, QFont.Weight.Bold)

        @classmethod
        def metric_large(cls) -> QFont:
            return cls.metric_huge()

        @classmethod
        def body(cls) -> QFont:
            return QFont(cls.FONT_FAMILY, 10)

        @classmethod
        def body_bold(cls) -> QFont:
            return QFont(cls.FONT_FAMILY, 10, QFont.Weight.Bold)

        @classmethod
        def caption(cls) -> QFont:
            return QFont(cls.FONT_FAMILY, 9)

    class Dimensions:
        """Dimensões padrão de layout e espaçamentos."""

        PAD_XS = 4
        PAD_S = 8
        PAD_M = 16
        PAD_L = 24
        PAD_XL = 32

        RADIUS_S = 6
        RADIUS_M = 12
        RADIUS_L = 16
        RADIUS_PILL = 20
        RADIUS_PANEL = RADIUS_M
        RADIUS_CARD = RADIUS_M
        RADIUS_BADGE = RADIUS_PILL

    class Styles:
        """Folhas de estilo QSS globais."""

        @classmethod
        def app_stylesheet(cls) -> str:
            return f"""
                QMainWindow, QWidget {{
                    background-color: {Theme.Colors.BG_DARK};
                    color: {Theme.Colors.TEXT_PRIMARY};
                    font-family: "{Theme.Fonts.FONT_FAMILY}";
                }}
                QScrollArea {{
                    border: none;
                    background-color: transparent;
                }}
                QScrollBar:vertical {{
                    border: none;
                    background: {Theme.Colors.BG_PANEL};
                    width: 6px;
                    border-radius: 3px;
                }}
                QScrollBar::handle:vertical {{
                    background: {Theme.Colors.BORDER};
                    border-radius: 3px;
                }}
                QLineEdit {{
                    background-color: {Theme.Colors.BG_INPUT};
                    color: {Theme.Colors.TEXT_PRIMARY};
                    border: 1px solid {Theme.Colors.BORDER};
                    border-radius: {Theme.Dimensions.RADIUS_S}px;
                    padding: 6px 10px;
                    font-size: 11px;
                }}
                QLineEdit:focus {{
                    border: 1px solid {Theme.Colors.PRIMARY};
                }}
            """
