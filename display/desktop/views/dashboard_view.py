"""
AeroTracker Core — Dashboard / Vista Principal Desktop
======================================================
Visualização inicial e resumo do status dos subsistemas.
"""

import customtkinter as ctk

from core.event_bus import Event, Events, event_bus
from core.module_manager import module_manager


class DashboardView(ctk.CTkFrame):
    """
    Painel de controle inicial exibindo cartões com resumos do sistema.
    """

    def __init__(self, parent: ctk.CTk) -> None:
        super().__init__(parent, corner_radius=10)

        # Título
        self.title_label = ctk.CTkLabel(
            self,
            text="✈ AeroTracker Core — Dashboard",
            font=ctk.CTkFont(size=22, weight="bold"),
        )
        self.title_label.pack(anchor="w", padx=20, pady=(20, 5))

        self.subtitle_label = ctk.CTkLabel(
            self,
            text="Plataforma de Monitoramento Aeroespacial em Tempo Real",
            font=ctk.CTkFont(size=14),
            text_color="gray",
        )
        self.subtitle_label.pack(anchor="w", padx=20, pady=(0, 15))

        # Grid de cartões de status
        self.cards_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.cards_frame.pack(fill="both", expand=True, padx=20, pady=10)

        self._render_cards()

        # Inscreve nos eventos do EventBus para atualizar o dashboard
        event_bus.subscribe(Events.AIRCRAFT_UPDATED, handler=self._on_aircraft_updated)
        event_bus.subscribe(Events.WEATHER_UPDATED, handler=self._on_weather_updated)

    def _render_cards(self) -> None:
        status = module_manager.status()

        # Grid 2x2
        self.cards_frame.grid_columnconfigure(0, weight=1)
        self.cards_frame.grid_columnconfigure(1, weight=1)
        self.cards_frame.grid_rowconfigure(0, weight=1)
        self.cards_frame.grid_rowconfigure(1, weight=1)

        # Cartão 1: Módulos
        c1 = ctk.CTkFrame(self.cards_frame, corner_radius=8)
        c1.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        ctk.CTkLabel(c1, text="📦 Módulos Ativos", font=ctk.CTkFont(size=16, weight="bold")).pack(padx=15, pady=(15, 5))
        ctk.CTkLabel(c1, text=f"{status['active']} / {status['total']}", font=ctk.CTkFont(size=28, weight="bold"), text_color="#1f538d").pack(padx=15, pady=10)

        # Cartão 2: Localização Base
        c2 = ctk.CTkFrame(self.cards_frame, corner_radius=8)
        c2.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        ctk.CTkLabel(c2, text="📍 Localização Base", font=ctk.CTkFont(size=16, weight="bold")).pack(padx=15, pady=(15, 5))
        ctk.CTkLabel(c2, text="São Paulo, BR", font=ctk.CTkFont(size=22, weight="bold"), text_color="#2fa572").pack(padx=15, pady=10)

        # Cartão 3: Radar de Aeronaves
        c3 = ctk.CTkFrame(self.cards_frame, corner_radius=8)
        c3.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        ctk.CTkLabel(c3, text="✈️ Radar de Aeronaves", font=ctk.CTkFont(size=16, weight="bold")).pack(padx=15, pady=(15, 5))
        self.lbl_aircraft_card = ctk.CTkLabel(c3, text="Aguardando dados...", font=ctk.CTkFont(size=22, weight="bold"), text_color="#e59400")
        self.lbl_aircraft_card.pack(padx=15, pady=10)

        # Cartão 4: Clima Local
        c4 = ctk.CTkFrame(self.cards_frame, corner_radius=8)
        c4.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")
        ctk.CTkLabel(c4, text="🌤 Clima Local", font=ctk.CTkFont(size=16, weight="bold")).pack(padx=15, pady=(15, 5))
        self.lbl_weather_card = ctk.CTkLabel(c4, text="Aguardando dados...", font=ctk.CTkFont(size=22, weight="bold"), text_color="#e59400")
        self.lbl_weather_card.pack(padx=15, pady=10)

    def _on_aircraft_updated(self, event: Event) -> None:
        data = event.data
        if not data:
            return

        total = 0
        if hasattr(data, "total_count"):
            total = data.total_count
        elif isinstance(data, dict):
            total = len(data.get("aircraft", []))

        text = f"{total} Detectadas"
        self.after(0, lambda: self.lbl_aircraft_card.configure(text=text, text_color="#1f538d"))

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
            self.after(0, lambda: self.lbl_weather_card.configure(text=text, text_color="#2fa572"))
