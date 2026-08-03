"""
AeroTracker Core — Radar de Aeronaves View Desktop
==================================================
Exibição e monitoramento do tráfego aéreo em tempo real.
Subcreve ao EventBus para atualizações reativas e dinâmicas na interface.
"""

import threading
import asyncio
from typing import Any, Optional

import customtkinter as ctk

from core.event_bus import Event, Events, event_bus
from models.aircraft import AircraftList, AircraftState
from utils.logger import get_logger

logger = get_logger(__name__)


class AircraftView(ctk.CTkFrame):
    """
    Interface reativa para exibição e consulta de aeronaves em tempo real.
    """

    def __init__(self, parent: ctk.CTk, aircraft_service: Any = None) -> None:
        super().__init__(parent, corner_radius=10)
        self.aircraft_service = aircraft_service

        # Top Bar (Header + Botão Atualizar)
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.pack(fill="x", padx=20, pady=(15, 5))

        self.title_label = ctk.CTkLabel(
            self.header_frame,
            text="📡 Radar de Aeronaves (OpenSky)",
            font=ctk.CTkFont(size=20, weight="bold"),
        )
        self.title_label.pack(side="left")

        self.btn_refresh = ctk.CTkButton(
            self.header_frame,
            text="🔄 Atualizar Agora",
            width=120,
            command=self._manual_refresh,
        )
        self.btn_refresh.pack(side="right")

        # Metadados de Status (Contadores)
        self.stats_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.stats_frame.pack(fill="x", padx=20, pady=(0, 10))

        self.lbl_stats = ctk.CTkLabel(
            self.stats_frame,
            text="Aguardando primeira leitura do radar...",
            font=ctk.CTkFont(size=13),
            text_color="gray",
        )
        self.lbl_stats.pack(anchor="w")

        # Container rolável de cards das aeronaves
        self.list_frame = ctk.CTkScrollableFrame(
            self, label_text="Aeronaves Detectadas na Região (250 km)"
        )
        self.list_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        # Inscreve no EventBus
        event_bus.subscribe(Events.AIRCRAFT_UPDATED, handler=self._on_aircraft_updated)

        # Se houver dados salvos/anteriores, exibe imediatamente
        if self.aircraft_service and self.aircraft_service.last_data:
            self._render_aircraft(self.aircraft_service.last_data)

    def _on_aircraft_updated(self, event: Event) -> None:
        """Handler do EventBus chamado quando novos dados de aeronaves chegam."""
        logger.debug("AircraftView: recebido evento de atualização de aeronaves")
        # Garante atualização thread-safe na UI usando self.after
        self.after(0, lambda: self._render_aircraft(event.data))

    def _manual_refresh(self) -> None:
        """Dispara atualização manual do serviço em thread separada."""
        if not self.aircraft_service:
            return

        self.btn_refresh.configure(state="disabled", text="⏳ Buscando...")
        self.lbl_stats.configure(text="Conectando à API OpenSky Network...", text_color="#1f538d")

        def _worker():
            try:
                asyncio.run(self.aircraft_service.update())
            finally:
                self.after(0, lambda: self.btn_refresh.configure(state="normal", text="🔄 Atualizar Agora"))

        threading.Thread(target=_worker, daemon=True).start()

    def _render_aircraft(self, data: Any) -> None:
        """Renderiza a lista de aeronaves na interface."""
        # Limpa widgets existentes no container
        for child in self.list_frame.winfo_children():
            child.destroy()

        if not data:
            self.lbl_stats.configure(text="Nenhum dado retornado do radar.", text_color="gray")
            ctk.CTkLabel(
                self.list_frame,
                text="Nenhuma aeronave encontrada no momento.",
                font=ctk.CTkFont(size=14),
                text_color="gray",
            ).pack(pady=30)
            return

        # Trata formato dict (storage) ou modelo Pydantic
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
            # Converter dicts em AircraftState para facilitar uso uniforme
            for a in raw_list:
                try:
                    aircraft_items.append(AircraftState(**a))
                except Exception:
                    pass
        else:
            total = 0
            airborne = 0
            on_ground = 0

        # Atualizar resumo do topo
        self.lbl_stats.configure(
            text=f"Total: {total} aeronaves | ✈️ Em voo: {airborne} | 🛬 Em solo: {on_ground}",
            text_color="#2fa572" if total > 0 else "gray",
        )

        if not aircraft_items:
            ctk.CTkLabel(
                self.list_frame,
                text="Nenhuma aeronave detectada dentro do raio de 250 km.",
                font=ctk.CTkFont(size=14),
                text_color="gray",
            ).pack(pady=30)
            return

        # Renderizar card para cada aeronave
        for ac in aircraft_items:
            self._create_aircraft_card(ac)

    def _create_aircraft_card(self, ac: AircraftState) -> None:
        """Cria um card visual estilizado para uma aeronave."""
        card = ctk.CTkFrame(self.list_frame, corner_radius=8)
        card.pack(fill="x", padx=5, pady=5)

        # Header do card: Callsign / Status
        head = ctk.CTkFrame(card, fg_color="transparent")
        head.pack(fill="x", padx=10, pady=(8, 4))

        callsign_text = f"✈  {ac.display_id}"
        ctk.CTkLabel(
            head,
            text=callsign_text,
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color="#1f538d" if not ac.on_ground else "#e59400",
        ).pack(side="left")

        status_text = "EM SOLO" if ac.on_ground else "EM VOO"
        status_color = "#e59400" if ac.on_ground else "#2fa572"
        ctk.CTkLabel(
            head,
            text=f"  ● {status_text}  ",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=status_color,
        ).pack(side="right")

        # Detalhes: País, Altitude, Velocidade, Proa, Posição
        details = ctk.CTkFrame(card, fg_color="transparent")
        details.pack(fill="x", padx=10, pady=(0, 8))

        country = ac.origin_country or "Desconhecido"
        alt_str = f"{ac.altitude_m:,.0f} m" if ac.altitude_m is not None else "N/A"
        speed_str = f"{ac.speed_kmh:,.0f} km/h" if ac.speed_kmh is not None else "N/A"
        heading_str = f"{ac.heading:.0f}°" if ac.heading is not None else "N/A"
        pos_str = str(ac.position) if ac.position else "Sem Posição GPS"

        info_line1 = f"🏳 {country}   |   📐 Altitude: {alt_str}   |   ⚡ Velocidade: {speed_str}"
        info_line2 = f"🧭 Proa: {heading_str}   |   📍 Posição: {pos_str}   |   ICAO24: {ac.icao24.upper()}"

        ctk.CTkLabel(
            details,
            text=info_line1,
            font=ctk.CTkFont(size=12),
            text_color="gray90",
        ).pack(anchor="w")

        ctk.CTkLabel(
            details,
            text=info_line2,
            font=ctk.CTkFont(size=11),
            text_color="gray70",
        ).pack(anchor="w")
