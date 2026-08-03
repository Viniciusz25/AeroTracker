"""
AeroTracker Core — Design System & Temas Visuais
===============================================
Centraliza todos os tokens visuais, paletas de cores, tipografia,
espaçamentos e estilos de componentes da interface gráfica.

Identidade Visual: Aerospace & High-Tech Deep Space
--------------------------------------------------
Dark Mode nativo com acentos de neon ciano, azul aeroespacial,
verde esmeralda para voos ativos e âmbar para alerta/solo.

Uso:
    from display.theme import Theme, StatusBadge, StyledCard

    color = Theme.Colors.PRIMARY
    font = Theme.Fonts.title()
"""

from typing import Any, Optional
import customtkinter as ctk


class Theme:
    """
    Design System central da aplicação AeroTracker.
    Define os tokens de design reutilizados em toda a interface.
    """

    class Colors:
        """Paleta de cores padronizada (Dark Mode High-Tech)."""

        # Planos de fundo principais
        BG_DARK = "#0B0E14"          # Fundo profundo principal
        SIDEBAR_BG = "#121722"       # Fundo da barra lateral
        CARD_BG = "#1A2130"          # Fundo dos cards e contêineres
        CARD_HOVER = "#222B3E"       # Hover de cards interativos
        HEADER_BG = "#161D2B"        # Fundo de cabeçalhos

        # Acentos de Marca (Brand Accents)
        PRIMARY = "#00D2FF"          # Ciano brilhante (Acento Principal)
        PRIMARY_HOVER = "#00A3CC"    # Ciano escuro hover
        SECONDARY = "#3A7BD5"        # Azul Aeroespacial
        SECONDARY_HOVER = "#2A5B9E"

        # Status Operacionais (Voo, Solo, Clima, Erros)
        AIRBORNE = "#00E676"         # Verde Esmeralda (Em Voo / Normal)
        AIRBORNE_BG = "#0A291B"      # Fundo do badge Em Voo
        ON_GROUND = "#FFB300"        # Âmbar (Em Solo / Alerta)
        ON_GROUND_BG = "#2E2408"     # Fundo do badge Em Solo
        ERROR = "#FF5252"            # Vermelho Alerta
        ERROR_BG = "#331212"

        # Tipografia & Texto
        TEXT_PRIMARY = "#F0F4F8"     # Branco suave de alto contraste
        TEXT_SECONDARY = "#94A3B8"   # Cinza azulado secundário
        TEXT_MUTED = "#64748B"       # Cinza atenuado para rodapés/datas

        # Bordas e Divisores
        BORDER = "#2A354B"           # Cor sutil de borda
        BORDER_LIGHT = "#3B4A66"

    class Fonts:
        """Tokens de Tipografia."""

        FONT_FAMILY = "Segoe UI"     # Fonte limpa e moderna nativa no Windows

        @classmethod
        def title_main(cls) -> ctk.CTkFont:
            return ctk.CTkFont(family=cls.FONT_FAMILY, size=24, weight="bold")

        @classmethod
        def title_section(cls) -> ctk.CTkFont:
            return ctk.CTkFont(family=cls.FONT_FAMILY, size=18, weight="bold")

        @classmethod
        def card_title(cls) -> ctk.CTkFont:
            return ctk.CTkFont(family=cls.FONT_FAMILY, size=15, weight="bold")

        @classmethod
        def body(cls) -> ctk.CTkFont:
            return ctk.CTkFont(family=cls.FONT_FAMILY, size=13, weight="normal")

        @classmethod
        def body_bold(cls) -> ctk.CTkFont:
            return ctk.CTkFont(family=cls.FONT_FAMILY, size=13, weight="bold")

        @classmethod
        def caption(cls) -> ctk.CTkFont:
            return ctk.CTkFont(family=cls.FONT_FAMILY, size=11, weight="normal")

        @classmethod
        def metric_large(cls) -> ctk.CTkFont:
            return ctk.CTkFont(family=cls.FONT_FAMILY, size=32, weight="bold")

        @classmethod
        def badge(cls) -> ctk.CTkFont:
            return ctk.CTkFont(family=cls.FONT_FAMILY, size=11, weight="bold")

    class Dimensions:
        """Espaçamentos, Raios e Tamanhos Padrão."""

        RADIUS_CARD = 12
        RADIUS_BUTTON = 8
        RADIUS_BADGE = 6

        PAD_XS = 4
        PAD_S = 8
        PAD_M = 16
        PAD_L = 24
        PAD_XL = 32


# ---------------------------------------------------------------------------
# Componentes Reutilizáveis do Design System
# ---------------------------------------------------------------------------


class StyledCard(ctk.CTkFrame):
    """
    Card padronizado do Design System com bordas sutis e fundo responsivo.
    """

    def __init__(self, parent: Any, **kwargs: Any) -> None:
        super().__init__(
            parent,
            fg_color=Theme.Colors.CARD_BG,
            border_color=Theme.Colors.BORDER,
            border_width=1,
            corner_radius=Theme.Dimensions.RADIUS_CARD,
            **kwargs,
        )


class StatusBadge(ctk.CTkFrame):
    """
    Badge visual reutilizável para indicar status (Ex: EM VOO, EM SOLO, ERRO, ATIVO).
    """

    def __init__(
        self,
        parent: Any,
        text: str,
        badge_type: str = "success",  # "success", "warning", "error", "info"
        **kwargs: Any,
    ) -> None:
        type_colors = {
            "success": (Theme.Colors.AIRBORNE, Theme.Colors.AIRBORNE_BG),
            "warning": (Theme.Colors.ON_GROUND, Theme.Colors.ON_GROUND_BG),
            "error": (Theme.Colors.ERROR, Theme.Colors.ERROR_BG),
            "info": (Theme.Colors.PRIMARY, "#0A2533"),
        }
        text_color, bg_color = type_colors.get(badge_type, type_colors["info"])

        super().__init__(
            parent,
            fg_color=bg_color,
            corner_radius=Theme.Dimensions.RADIUS_BADGE,
            border_color=text_color,
            border_width=1,
            **kwargs,
        )

        self.label = ctk.CTkLabel(
            self,
            text=f" {text} ",
            font=Theme.Fonts.badge(),
            text_color=text_color,
        )
        self.label.pack(padx=Theme.Dimensions.PAD_S, pady=2)


class PrimaryButton(ctk.CTkButton):
    """
    Botão primário estilizado do Design System.
    """

    def __init__(self, parent: Any, text: str, command: Optional[Any] = None, **kwargs: Any) -> None:
        super().__init__(
            parent,
            text=text,
            command=command,
            fg_color=Theme.Colors.PRIMARY,
            hover_color=Theme.Colors.PRIMARY_HOVER,
            text_color="#000000",
            font=Theme.Fonts.body_bold(),
            corner_radius=Theme.Dimensions.RADIUS_BUTTON,
            height=36,
            **kwargs,
        )


class SecondaryButton(ctk.CTkButton):
    """
    Botão secundário estilizado do Design System.
    """

    def __init__(self, parent: Any, text: str, command: Optional[Any] = None, **kwargs: Any) -> None:
        super().__init__(
            parent,
            text=text,
            command=command,
            fg_color=Theme.Colors.CARD_BG,
            hover_color=Theme.Colors.CARD_HOVER,
            text_color=Theme.Colors.TEXT_PRIMARY,
            border_color=Theme.Colors.BORDER_LIGHT,
            border_width=1,
            font=Theme.Fonts.body(),
            corner_radius=Theme.Dimensions.RADIUS_BUTTON,
            height=36,
            **kwargs,
        )
