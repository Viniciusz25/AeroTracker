"""
AeroTracker Core — Glass Cockpit & Avionics Design System
===========================================================
Estilo visual inspirado em Glass Cockpit (Garmin G1000, Boeing ND, Airbus FBW),
sistemas de controle de tráfego aéreo (ATC Radar) e Mission Control NASA.

Especificações do Estilo:
    - Fundo: Preto profundo (#000000 / #05070A)
    - Cores Principais: Azul Neon (#0088FF), Ciano (#00F0FF), Branco (#F8FAFC), Cinza Escuro (#121824)
    - Semântica Restrita:
        * Verde (#00FF66): Informações positivas/normais (Em voo, OK, Ativo)
        * Laranja/Âmbar (#FFB300): Atenção/Solo/Standby
        * Vermelho (#FF3333): Alertas/Emergência
"""

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QFont


class Theme:
    """
    Tokens visuais centralizados do Design System Glass Cockpit.
    """

    class Colors:
        """Paleta de cores técnica estilo instrumento aeroespacial."""

        # Planos de Fundo (Deep Black Glass Cockpit)
        BG_DARK = "#000000"          # Preto absoluto para o fundo principal
        BG_SIDEBAR = "#05070A"       # Painel de controle lateral
        BG_PANEL = "#0B0F17"         # Moldura dos instrumentos
        BG_CARD = "#101622"          # Fundo dos cartões de instrumentos
        BG_CARD_HOVER = "#182234"    # Highlight discreto no hover

        # Acentos de Marca (Neon & Ciano Aeroespacial)
        CYAN_NEON = "#00F0FF"        # Ciano primário (Vores, texto em destaque)
        BLUE_NEON = "#0088FF"        # Azul de navegação (Linhas de rota, bússola)
        BORDER = "#1E293B"           # Bordas finas de precisão
        BORDER_HIGHLIGHT = "#00F0FF" # Borda ativa/selecionada

        # Status Semânticos Restritos
        POSITIVE = "#00FF66"         # Verde (Voo ativo, normal, online)
        POSITIVE_BG = "#042010"
        ATTENTION = "#FFB300"        # Âmbar (Solo, atenção, alerta sutil)
        ATTENTION_BG = "#261A02"
        ALERT = "#FF3333"            # Vermelho (Emergência, erro crítico)
        ALERT_BG = "#290808"

        # Aliases de compatibilidade
        PRIMARY = CYAN_NEON
        SECONDARY = BLUE_NEON
        AIRBORNE = POSITIVE
        ON_GROUND = ATTENTION
        ERROR = ALERT

        # Tipografia de Alto Contraste
        TEXT_PRIMARY = "#F8FAFC"     # Branco puro
        TEXT_SECONDARY = "#94A3B8"   # Cinza claro técnico
        TEXT_MUTED = "#475569"       # Cinza fosco (Legendas, rótulos)

        @classmethod
        def qcolor(cls, hex_code: str) -> QColor:
            """Retorna QColor a partir do código hexadecimal."""
            return QColor(hex_code)

    class Fonts:
        """Tipografia fina de alta legibilidade para cockpits."""

        FONT_FAMILY = "Segoe UI"
        FONT_MONO = "Consolas"

        @classmethod
        def title_display(cls) -> QFont:
            font = QFont(cls.FONT_FAMILY, 18, QFont.Weight.Bold)
            return font

        @classmethod
        def title_main(cls) -> QFont:
            return cls.title_display()

        @classmethod
        def title_section(cls) -> QFont:
            font = QFont(cls.FONT_FAMILY, 14, QFont.Weight.Bold)
            return font

        @classmethod
        def section_header(cls) -> QFont:
            return cls.title_section()

        @classmethod
        def card_title(cls) -> QFont:
            font = QFont(cls.FONT_FAMILY, 11, QFont.Weight.Bold)
            return font

        @classmethod
        def metric_huge(cls) -> QFont:
            font = QFont(cls.FONT_MONO, 24, QFont.Weight.Bold)
            return font

        @classmethod
        def metric_large(cls) -> QFont:
            return cls.metric_huge()

        @classmethod
        def body(cls) -> QFont:
            return QFont(cls.FONT_FAMILY, 10)

        @classmethod
        def body_bold(cls) -> QFont:
            font = QFont(cls.FONT_FAMILY, 10, QFont.Weight.Bold)
            return font

        @classmethod
        def caption(cls) -> QFont:
            return QFont(cls.FONT_MONO, 9)

    class Dimensions:
        """Espaçamentos limpos e raios discretos de instrumento."""

        RADIUS_PANEL = 6
        RADIUS_BADGE = 4

        PAD_XS = 4
        PAD_S = 8
        PAD_M = 16
        PAD_L = 24

    class Styles:
        """Folhas de estilo QSS globais de instrumento aeroespacial."""

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
                    width: 6px;
                    border-radius: 3px;
                }}
                QScrollBar::handle:vertical {{
                    background: {Theme.Colors.BORDER};
                    border-radius: 3px;
                    min-height: 20px;
                }}
                QScrollBar::handle:vertical:hover {{
                    background: {Theme.Colors.CYAN_NEON};
                }}
                QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                    height: 0px;
                }}
            """
