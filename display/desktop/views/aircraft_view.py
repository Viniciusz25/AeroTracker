"""
AeroTracker Core — Radar de Aeronaves View Desktop
==================================================
Exibição e monitoramento do tráfego aéreo em tempo real utilizando o Design System.
"""

import asyncio
import threading
from typing import Any

import customtkinter as ctk

from core.event_bus import Event, Events, event_bus
from display.theme import PrimaryButton, StatusBadge, StyledCard, Theme
from models.aircraft import AircraftList, AircraftState
from utils.logger import get_logger

logger = get_logger(__name__)


class AircraftView(ctk.CTkFrame):
    """
    Interface reativa para exibição e consulta de aeronaves em tempo real.
    Conectada ao Design System.
    """

    def __init__(self, parent: ctk.CTk, aircraft_service: Any = None) -> None:
        super().__init__(parent, fg_color="transparent")
        self.aircraft_service = aircraft_service

        # Top Bar (Header + Botão Atualizar)
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.pack(fill="x", padx=Theme.Dimensions.PAD_M, pady=(Theme.Dimensions.PAD_M, Theme.Dimensions.PAD_S))

        self.title_label = ctk.CTkLabel(
            self.header_frame,
            text="📡 Radar de Aeronaves",
            font=Theme.Fonts.title_section(),
            text_color=Theme.Colors.TEXT_PRIMARY,
        )
        self.title_label.pack(side="left")

        self.btn_refresh = PrimaryButton(
            self.header_frame,
            text="🔄 Atualizar Agora",
            width=140,
            command=self._manual_refresh,
        )
        self.btn_refresh.pack(side="right")

        # Metadados de Status (Contadores)
        self.stats_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.stats_frame.pack(fill="x", padx=Theme.Dimensions.PAD_M, pady=(0, Theme.Dimensions.PAD_S))

        self.lbl_stats = ctk.CTkLabel(
            self.stats_frame,
            text="Aguardando primeira leitura do radar...",
            font=Theme.Fonts.body(),
            text_color=Theme.Colors.TEXT_SECONDARY,
        )
        self.lbl_stats.pack(anchor="w")

        # Container rolável de cards das aeronaves
        self.list_frame = ctk.CTkScrollableFrame(
            self,
            label_text="Aeronaves Detectadas na Região (250 km)",
            label_text_color=Theme.Colors.TEXT_SECONDARY,
            label_font=Theme.Fonts.body_bold(),
            fg_color=Theme.Colors.BG_DARK,
            border_color=Theme.Colors.BORDER,
            border_width=1,
            corner_radius=Theme.Dimensions.RADIUS_CARD,
        )
        self.list_frame.pack(fill="both", expand=True, padx=Theme.Dimensions.PAD_M, pady=(0, Theme.Dimensions.PAD_M))

        # Inscreve no EventBus
        event_bus.subscribe(Events.AIRCRAFT_UPDATED, handler=self._on_aircraft_updated)

        # Exibe dados imediatamente se já existirem no serviço
        if self.aircraft_service and self.aircraft_service.last_data:
            self._render_aircraft(self.aircraft_service.last_data)

    def _on_aircraft_updated(self, event: Event) -> None:
        """Handler chamado via EventBus quando chegam novos dados de aeronaves."""
        logger.debug("AircraftView: recebido evento de atualização de aeronaves")
        self.after(0, lambda: self._render_aircraft(event.data))

    def _manual_refresh(self) -> None:
        """Dispara atualização manual do serviço em thread de segundo plano."""
        if not self.aircraft_service:
            return

        self.btn_refresh.configure(state="disabled", text="⏳ Buscando...")
        self.lbl_stats.configure(text="Conectando à API OpenSky Network...", text_color=Theme.Colors.PRIMARY)

        def _worker():
            try:
                asyncio.run(self.aircraft_service.update())
            finally:
                self.after(0, lambda: self.btn_refresh.configure(state="normal", text="🔄 Atualizar Agora"))

        threading.Thread(target=_worker, daemon=True).start()

    def _render_aircraft(self, data: Any) -> None:
        """Renderiza a lista de aeronaves utilizando o Design System."""
        for child in self.list_frame.winfo_children():
            child.destroy()

        if not data:
            self.lbl_stats.configure(text="Nenhum dado retornado do radar.", text_color=Theme.Colors.TEXT_MUTED)
            ctk.CTkLabel(
                self.list_frame,
                text="Nenhuma aeronave encontrada no momento.",
                font=Theme.Fonts.body(),
                text_color=Theme.Colors.TEXT_SECONDARY,
            ).pack(pady=Theme.Dimensions.PAD_XL)
            return

        aircraft_items = []
        if isinstance(data, AircraftList):
            aircraft_items = data.aircraft
            total = data.total_count
            airborne = data.airborne_count
            on_ground = data.on_ground_count
        elif isinstance(data, dict):
            raw_list = data.get("aircraft", [])
            total = len(raw_list)
            airborne = sum(1 for a in raw_list if not a.get("on_ground", False))
            on_ground = total - airborne
            for a in raw_list:
                try:
                    aircraft_items.append(AircraftState(**a))
                except Exception:
                    pass
        else:
            total = 0
            airborne = 0
            on_ground = 0

        self.lbl_stats.configure(
            text=f"Total: {total} aeronaves   |   ✈️ Em voo: {airborne}   |   🛬 Em solo: {on_ground}",
            text_color=Theme.Colors.PRIMARY if total > 0 else Theme.Colors.TEXT_MUTED,
        )

        if not aircraft_items:
            ctk.CTkLabel(
                self.list_frame,
                text="Nenhuma aeronave detectada dentro do raio de 250 km.",
                font=Theme.Fonts.body(),
                text_color=Theme.Colors.TEXT_MUTED,
            ).pack(pady=Theme.Dimensions.PAD_XL)
            return

        for ac in aircraft_items:
            self._create_aircraft_card(ac)

    def _create_aircraft_card(self, ac: AircraftState) -> None:
        """Cria um StyledCard para representar a aeronave."""
        card = StyledCard(self.list_frame)
        card.pack(fill="x", padx=Theme.Dimensions.PAD_S, pady=Theme.Dimensions.PAD_S)

        # Header do Card: Callsign e Badge de Status
        head = ctk.CTkFrame(card, fg_color="transparent")
        head.pack(fill="x", padx=Theme.Dimensions.PAD_M, pady=(Theme.Dimensions.PAD_S, Theme.Dimensions.PAD_XS))

        callsign_text = f"✈  {ac.display_id}"
        ctk.CTkLabel(
            head,
            text=callsign_text,
            font=Theme.Fonts.card_title(),
            text_color=Theme.Colors.TEXT_PRIMARY,
        ).pack(side="left")

        badge_type = "warning" if ac.on_ground else "success"
        status_text = "EM SOLO" if ac.on_ground else "EM VOO"
        badge = StatusBadge(head, text=status_text, badge_type=badge_type)
        badge.pack(side="right")

        # Corpo do Card: Informações Técnicas
        details = ctk.CTkFrame(card, fg_color="transparent")
        details.pack(fill="x", padx=Theme.Dimensions.PAD_M, pady=(0, Theme.Dimensions.PAD_S))

        country = ac.origin_country or "Desconhecido"
        alt_str = f"{ac.altitude_m:,.0f} m" if ac.altitude_m is not None else "N/A"
        speed_str = f"{ac.speed_kmh:,.0f} km/h" if ac.speed_kmh is not None else "N/A"
        heading_str = f"{ac.heading:.0f}°" if ac.heading is not None else "N/A"
        pos_str = str(ac.position) if ac.position else "Sem GPS"

        info_line1 = f"🏳 {country}   |   📐 Altitude: {alt_str}   |   ⚡ Velocidade: {speed_str}"
        info_line2 = f"🧭 Proa: {heading_str}   |   📍 GPS: {pos_str}   |   Transponder: {ac.icao24.upper()}"

        ctk.CTkLabel(
            details,
            text=info_line1,
            font=Theme.Fonts.body(),
            text_color=Theme.Colors.TEXT_PRIMARY,
        ).pack(anchor="w")

        ctk.CTkLabel(
            details,
            text=info_line2,
            font=Theme.Fonts.caption(),
            text_color=Theme.Colors.TEXT_SECONDARY,
        ).pack(anchor="w")
