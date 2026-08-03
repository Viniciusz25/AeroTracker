"""
AeroTracker Core — Janela Principal Desktop
============================================
Aplicação CustomTkinter com menu lateral de navegação e container central.
"""

from typing import Any, Optional

import customtkinter as ctk

from display.desktop.views.aircraft_view import AircraftView
from display.desktop.views.dashboard_view import DashboardView
from display.desktop.views.weather_view import WeatherView
from utils.logger import get_logger

logger = get_logger(__name__)

# Configuração de tema
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")


class MainWindow(ctk.CTk):
    """
    Janela principal da interface Desktop.

    Args:
        services: Dicionário com instâncias dos serviços do sistema.
    """

    def __init__(self, services: Optional[dict[str, Any]] = None) -> None:
        super().__init__()
        self.services = services or {}

        self.title("AeroTracker Core — Estação de Monitoramento")
        self.geometry("1100x680")
        self.minsize(900, 550)

        # Layout Principal (Sidebar + View Central)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # ---------------------------------------------------------------------
        # Menu Lateral (Sidebar)
        # ---------------------------------------------------------------------
        self.sidebar_frame = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(5, weight=1)

        self.logo_label = ctk.CTkLabel(
            self.sidebar_frame,
            text="AeroTracker",
            font=ctk.CTkFont(size=20, weight="bold"),
        )
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 20))

        # Botões de Navegação
        self.btn_dashboard = ctk.CTkButton(
            self.sidebar_frame, text="📊 Dashboard", command=self._show_dashboard
        )
        self.btn_dashboard.grid(row=1, column=0, padx=20, pady=10)

        self.btn_aircraft = ctk.CTkButton(
            self.sidebar_frame, text="✈ Radar Aeronaves", command=self._show_aircraft
        )
        self.btn_aircraft.grid(row=2, column=0, padx=20, pady=10)

        self.btn_weather = ctk.CTkButton(
            self.sidebar_frame, text="🌤 Clima", command=self._show_weather
        )
        self.btn_weather.grid(row=3, column=0, padx=20, pady=10)

        # ---------------------------------------------------------------------
        # Área Principal (Container de Views)
        # ---------------------------------------------------------------------
        self.views: dict[str, ctk.CTkFrame] = {
            "dashboard": DashboardView(self),
            "aircraft": AircraftView(self, aircraft_service=self.services.get("aircraft")),
            "weather": WeatherView(self, weather_service=self.services.get("weather")),
        }

        self._active_view_name = "dashboard"
        self.views["dashboard"].grid(row=0, column=1, padx=20, pady=20, sticky="nsew")

    def _show_view(self, name: str) -> None:
        """Alterna a exibição para a view informada."""
        if name not in self.views:
            return

        # Oculta a view atual
        self.views[self._active_view_name].grid_forget()

        # Exibe a nova view
        self.views[name].grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        self._active_view_name = name

    def _show_dashboard(self) -> None:
        self._show_view("dashboard")

    def _show_aircraft(self) -> None:
        self._show_view("aircraft")

    def _show_weather(self) -> None:
        self._show_view("weather")
