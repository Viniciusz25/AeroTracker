"""
AeroTracker Core — Clima View Desktop
=====================================
Exibição de informações meteorológicas com o Design System.
"""

import asyncio
import threading
from typing import Any

import customtkinter as ctk

from core.event_bus import Event, Events, event_bus
from display.theme import PrimaryButton, StyledCard, Theme
from models.weather import WeatherSnapshot
from utils.logger import get_logger

logger = get_logger(__name__)


class WeatherView(ctk.CTkFrame):
    """
    Interface para consulta meteorológica em tempo real integrada ao Design System.
    """

    def __init__(self, parent: ctk.CTk, weather_service: Any = None) -> None:
        super().__init__(parent, fg_color="transparent")
        self.weather_service = weather_service

        # Top Bar
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.pack(fill="x", padx=Theme.Dimensions.PAD_M, pady=(Theme.Dimensions.PAD_M, Theme.Dimensions.PAD_S))

        self.title_label = ctk.CTkLabel(
            self.header_frame,
            text="🌤 Condições Meteorológicas",
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

        # Container principal
        self.content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.content_frame.pack(fill="both", expand=True, padx=Theme.Dimensions.PAD_M, pady=Theme.Dimensions.PAD_S)

        # Inscrição no EventBus
        event_bus.subscribe(Events.WEATHER_UPDATED, handler=self._on_weather_updated)

        if self.weather_service and self.weather_service.last_data:
            self._render_weather(self.weather_service.last_data)
        else:
            self.lbl_placeholder = ctk.CTkLabel(
                self.content_frame,
                text="Aguardando primeira leitura meteorológica...",
                font=Theme.Fonts.body(),
                text_color=Theme.Colors.TEXT_MUTED,
            )
            self.lbl_placeholder.pack(pady=Theme.Dimensions.PAD_XL)

    def _on_weather_updated(self, event: Event) -> None:
        self.after(0, lambda: self._render_weather(event.data))

    def _manual_refresh(self) -> None:
        if not self.weather_service:
            return

        self.btn_refresh.configure(state="disabled", text="⏳ Buscando...")

        def _worker():
            try:
                asyncio.run(self.weather_service.update())
            finally:
                self.after(0, lambda: self.btn_refresh.configure(state="normal", text="🔄 Atualizar Agora"))

        threading.Thread(target=_worker, daemon=True).start()

    def _render_weather(self, data: Any) -> None:
        for child in self.content_frame.winfo_children():
            child.destroy()

        if not data:
            ctk.CTkLabel(self.content_frame, text="Sem dados de clima.", font=Theme.Fonts.body(), text_color=Theme.Colors.TEXT_MUTED).pack(pady=Theme.Dimensions.PAD_XL)
            return

        if isinstance(data, WeatherSnapshot):
            location = data.location_name
            temp = f"{data.temperature_c:.1f} °C"
            feels = f"{data.feels_like_c:.1f} °C" if data.feels_like_c is not None else "--"
            humidity = f"{data.humidity_pct:.0f} %"
            pressure = f"{data.pressure_hpa:.0f} hPa"
            cond_desc = data.condition.description.capitalize() if data.condition else "--"
            wind_speed = f"{data.wind.speed.in_kmh:.1f} km/h" if data.wind and data.wind.speed else "--"
            wind_dir = data.wind.direction_name if data.wind else "--"
        elif isinstance(data, dict):
            location = data.get("location_name", "Desconhecido")
            temp = f"{data.get('temperature_c', 0):.1f} °C"
            feels = f"{data.get('feels_like_c', 0):.1f} °C"
            humidity = f"{data.get('humidity_pct', 0):.0f} %"
            pressure = f"{data.get('pressure_hpa', 1013):.0f} hPa"
            cond_desc = data.get("condition", {}).get("description", "--").capitalize()
            wind_speed = "--"
            wind_dir = "--"
        else:
            return

        # Main Card
        card = StyledCard(self.content_frame)
        card.pack(fill="x", padx=Theme.Dimensions.PAD_S, pady=Theme.Dimensions.PAD_S)

        ctk.CTkLabel(card, text=f"📍 {location}", font=Theme.Fonts.title_section(), text_color=Theme.Colors.TEXT_PRIMARY).pack(padx=Theme.Dimensions.PAD_M, pady=(Theme.Dimensions.PAD_M, Theme.Dimensions.PAD_XS))
        ctk.CTkLabel(card, text=temp, font=Theme.Fonts.metric_large(), text_color=Theme.Colors.AIRBORNE).pack(padx=Theme.Dimensions.PAD_M, pady=Theme.Dimensions.PAD_S)
        ctk.CTkLabel(card, text=f"Condição: {cond_desc}", font=Theme.Fonts.body_bold(), text_color=Theme.Colors.PRIMARY).pack(padx=Theme.Dimensions.PAD_M, pady=(0, Theme.Dimensions.PAD_S))

        # Metrics grid
        grid = ctk.CTkFrame(card, fg_color="transparent")
        grid.pack(fill="x", padx=Theme.Dimensions.PAD_M, pady=(0, Theme.Dimensions.PAD_M))

        ctk.CTkLabel(grid, text=f"🌡 Sensação: {feels}", font=Theme.Fonts.body(), text_color=Theme.Colors.TEXT_PRIMARY).grid(row=0, column=0, padx=Theme.Dimensions.PAD_S, pady=Theme.Dimensions.PAD_XS, sticky="w")
        ctk.CTkLabel(grid, text=f"💧 Umidade: {humidity}", font=Theme.Fonts.body(), text_color=Theme.Colors.TEXT_PRIMARY).grid(row=0, column=1, padx=Theme.Dimensions.PAD_S, pady=Theme.Dimensions.PAD_XS, sticky="w")
        ctk.CTkLabel(grid, text=f"💨 Vento: {wind_speed} ({wind_dir})", font=Theme.Fonts.body(), text_color=Theme.Colors.TEXT_PRIMARY).grid(row=1, column=0, padx=Theme.Dimensions.PAD_S, pady=Theme.Dimensions.PAD_XS, sticky="w")
        ctk.CTkLabel(grid, text=f"⏲ Pressão: {pressure}", font=Theme.Fonts.body(), text_color=Theme.Colors.TEXT_PRIMARY).grid(row=1, column=1, padx=Theme.Dimensions.PAD_S, pady=Theme.Dimensions.PAD_XS, sticky="w")
