"""
AeroTracker Core — Clima View Desktop
=====================================
Exibição de informações meteorológicas em tempo real.
"""

import threading
import asyncio
from typing import Any

import customtkinter as ctk

from core.event_bus import Event, Events, event_bus
from models.weather import WeatherSnapshot
from utils.logger import get_logger

logger = get_logger(__name__)


class WeatherView(ctk.CTkFrame):
    """
    Interface para consulta meteorológica em tempo real.
    """

    def __init__(self, parent: ctk.CTk, weather_service: Any = None) -> None:
        super().__init__(parent, corner_radius=10)
        self.weather_service = weather_service

        # Top Bar
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.pack(fill="x", padx=20, pady=(15, 5))

        self.title_label = ctk.CTkLabel(
            self.header_frame,
            text="🌤 Condições Meteorológicas (OpenWeather)",
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

        # Container principal
        self.content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.content_frame.pack(fill="both", expand=True, padx=20, pady=10)

        # Inscrição no EventBus
        event_bus.subscribe(Events.WEATHER_UPDATED, handler=self._on_weather_updated)

        if self.weather_service and self.weather_service.last_data:
            self._render_weather(self.weather_service.last_data)
        else:
            self.lbl_placeholder = ctk.CTkLabel(
                self.content_frame, text="Aguardando primeira leitura meteorológica...", text_color="gray"
            )
            self.lbl_placeholder.pack(pady=30)

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
            ctk.CTkLabel(self.content_frame, text="Sem dados de clima.", text_color="gray").pack(pady=30)
            return

        # Tratar objeto ou dict
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
        card = ctk.CTkFrame(self.content_frame, corner_radius=10)
        card.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(card, text=f"📍 {location}", font=ctk.CTkFont(size=18, weight="bold")).pack(padx=20, pady=(15, 5))
        ctk.CTkLabel(card, text=temp, font=ctk.CTkFont(size=36, weight="bold"), text_color="#2fa572").pack(padx=20, pady=5)
        ctk.CTkLabel(card, text=f"Condição: {cond_desc}", font=ctk.CTkFont(size=14, weight="bold")).pack(padx=20, pady=(0, 10))

        # Metrics grid
        grid = ctk.CTkFrame(card, fg_color="transparent")
        grid.pack(fill="x", padx=20, pady=(0, 15))

        ctk.CTkLabel(grid, text=f"🌡 Sensação: {feels}", font=ctk.CTkFont(size=12)).grid(row=0, column=0, padx=10, pady=5, sticky="w")
        ctk.CTkLabel(grid, text=f"💧 Umidade: {humidity}", font=ctk.CTkFont(size=12)).grid(row=0, column=1, padx=10, pady=5, sticky="w")
        ctk.CTkLabel(grid, text=f"💨 Vento: {wind_speed} ({wind_dir})", font=ctk.CTkFont(size=12)).grid(row=1, column=0, padx=10, pady=5, sticky="w")
        ctk.CTkLabel(grid, text=f"⏲ Pressão: {pressure}", font=ctk.CTkFont(size=12)).grid(row=1, column=1, padx=10, pady=5, sticky="w")
