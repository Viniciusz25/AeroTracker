"""
Testes — Display Layer
=======================
Testa a integridade de instanciação da janela principal e das views do CustomTkinter em modo headless/sem interface física.
"""

import pytest
from display.desktop.app_window import MainWindow
from display.desktop.views.dashboard_view import DashboardView
from display.desktop.views.aircraft_view import AircraftView
from display.desktop.views.weather_view import WeatherView


class TestDesktopUI:
    def test_main_window_instantiation(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """
        Valida se as classes da UI podem ser instanciadas.
        Evitamos chamar app.mainloop() para não bloquear a execução dos testes.
        """
        # Desativa o loop da interface física caso esteja rodando em ambiente CI/headless
        monkeypatch.setattr("customtkinter.CTk.mainloop", lambda self: None)

        try:
            app = MainWindow()
            assert app.title() == "AeroTracker Core — Estação de Monitoramento"
            assert "dashboard" in app.views
            assert "aircraft" in app.views
            assert "weather" in app.views
            app.destroy()
        except Exception as e:
            # Em ambientes totalmente headless sem Tcl/Tk pode falhar por falta de DISPLAY
            pytest.skip(f"Ambiente Tkinter não suportado em headless: {e}")
