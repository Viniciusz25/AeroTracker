"""
AeroTracker Core — Dashboard View Desktop
==========================================
Visualização principal e resumo do sistema com o Design System.
"""

import customtkinter as ctk

from core.event_bus import Event, Events, event_bus
from core.module_manager import module_manager
from display.theme import StatusBadge, StyledCard, Theme


class DashboardView(ctk.CTkFrame):
    """
    Painel de controle principal do AeroTracker Core.
    """

    def __init__(self, parent: ctk.CTk) -> None:
        super().__init__(parent, fg_color="transparent")

        # Título da Página
        self.title_label = ctk.CTkLabel(
            self,
            text="✈ AeroTracker Core — Dashboard",
            font=Theme.Fonts.title_main(),
            text_color=Theme.Colors.TEXT_PRIMARY,
        )
        self.title_label.pack(anchor="w", padx=Theme.Dimensions.PAD_M, pady=(Theme.Dimensions.PAD_M, Theme.Dimensions.PAD_XS))

        self.subtitle_label = ctk.CTkLabel(
            self,
            text="Plataforma Integrada de Monitoramento Aeroespacial",
            font=Theme.Fonts.body(),
            text_color=Theme.Colors.TEXT_SECONDARY,
        )
        self.subtitle_label.pack(anchor="w", padx=Theme.Dimensions.PAD_M, pady=(0, Theme.Dimensions.PAD_L))

        # Grid de cartões de status
        self.cards_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.cards_frame.pack(fill="both", expand=True, padx=Theme.Dimensions.PAD_M, pady=Theme.Dimensions.PAD_S)

        self._render_cards()

        # Inscrições no EventBus
        event_bus.subscribe(Events.AIRCRAFT_UPDATED, handler=self._on_aircraft_updated)
        event_bus.subscribe(Events.WEATHER_UPDATED, handler=self._on_weather_updated)

    def _render_cards(self) -> None:
        status = module_manager.status()

        self.cards_frame.grid_columnconfigure(0, weight=1)
        self.cards_frame.grid_columnconfigure(1, weight=1)
        self.cards_frame.grid_rowconfigure(0, weight=1)
        self.cards_frame.grid_rowconfigure(1, weight=1)

        # Cartão 1: Módulos
        c1 = StyledCard(self.cards_frame)
        c1.grid(row=0, column=0, padx=Theme.Dimensions.PAD_S, pady=Theme.Dimensions.PAD_S, sticky="nsew")
        ctk.CTkLabel(c1, text="📦 Módulos Ativos", font=Theme.Fonts.card_title(), text_color=Theme.Colors.TEXT_PRIMARY).pack(padx=Theme.Dimensions.PAD_M, pady=(Theme.Dimensions.PAD_M, Theme.Dimensions.PAD_XS))
        ctk.CTkLabel(c1, text=f"{status['active']} / {status['total']}", font=Theme.Fonts.metric_large(), text_color=Theme.Colors.PRIMARY).pack(padx=Theme.Dimensions.PAD_M, pady=Theme.Dimensions.PAD_S)

        # Cartão 2: Localização Base
        c2 = StyledCard(self.cards_frame)
        c2.grid(row=0, column=1, padx=Theme.Dimensions.PAD_S, pady=Theme.Dimensions.PAD_S, sticky="nsew")
        ctk.CTkLabel(c2, text="📍 Localização Base", font=Theme.Fonts.card_title(), text_color=Theme.Colors.TEXT_PRIMARY).pack(padx=Theme.Dimensions.PAD_M, pady=(Theme.Dimensions.PAD_M, Theme.Dimensions.PAD_XS))
        ctk.CTkLabel(c2, text="São Paulo, BR", font=Theme.Fonts.title_section(), text_color=Theme.Colors.AIRBORNE).pack(padx=Theme.Dimensions.PAD_M, pady=Theme.Dimensions.PAD_S)

        # Cartão 3: Radar de Aeronaves
        c3 = StyledCard(self.cards_frame)
        c3.grid(row=1, column=0, padx=Theme.Dimensions.PAD_S, pady=Theme.Dimensions.PAD_S, sticky="nsew")
        ctk.CTkLabel(c3, text="✈️ Radar de Aeronaves", font=Theme.Fonts.card_title(), text_color=Theme.Colors.TEXT_PRIMARY).pack(padx=Theme.Dimensions.PAD_M, pady=(Theme.Dimensions.PAD_M, Theme.Dimensions.PAD_XS))
        self.lbl_aircraft_card = ctk.CTkLabel(c3, text="Aguardando dados...", font=Theme.Fonts.title_section(), text_color=Theme.Colors.ON_GROUND)
        self.lbl_aircraft_card.pack(padx=Theme.Dimensions.PAD_M, pady=Theme.Dimensions.PAD_S)

        # Cartão 4: Clima Local
        c4 = StyledCard(self.cards_frame)
        c4.grid(row=1, column=1, padx=Theme.Dimensions.PAD_S, pady=Theme.Dimensions.PAD_S, sticky="nsew")
        ctk.CTkLabel(c4, text="🌤 Clima Local", font=Theme.Fonts.card_title(), text_color=Theme.Colors.TEXT_PRIMARY).pack(padx=Theme.Dimensions.PAD_M, pady=(Theme.Dimensions.PAD_M, Theme.Dimensions.PAD_XS))
        self.lbl_weather_card = ctk.CTkLabel(c4, text="Aguardando dados...", font=Theme.Fonts.title_section(), text_color=Theme.Colors.ON_GROUND)
        self.lbl_weather_card.pack(padx=Theme.Dimensions.PAD_M, pady=Theme.Dimensions.PAD_S)

    def _on_aircraft_updated(self, event: Event) -> None:
        data = event.data
        if not data:
            return

        total = 0
        if hasattr(data, "total_count"):
            total = data.total_count
        elif isinstance(data, dict):
            total = len(data.get("aircraft", []))

        text = f"{total} Aeronaves Detectadas"
        self.after(0, lambda: self.lbl_aircraft_card.configure(text=text, text_color=Theme.Colors.PRIMARY))

    def _on_weather_updated(self, event: Event) -> None:
        data = event.data
        if not data:
            return

        temp = None
        if hasattr(data, "temperature_c"):
            temp = data.temperature_c
        elif isinstance(data, dict):
            temp = data.get("temperature_c")

        if temp is not None:
            text = f"{temp:.1f} °C"
            self.after(0, lambda: self.lbl_weather_card.configure(text=text, text_color=Theme.Colors.AIRBORNE))
