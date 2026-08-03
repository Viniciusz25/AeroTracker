"""
AeroTracker Core — Weather Model (MVC)
======================================
Modelo de dados da tela de Clima.
Todos os textos e medições derivam desta classe.
"""

from PySide6.QtCore import QObject, Signal
from models.weather import WeatherSnapshot


class WeatherModel(QObject):
    """
    Model da tela de Clima.
    """

    data_changed = Signal()

    def __init__(self) -> None:
        super().__init__()
        self._title_text = "🌤 Condições Meteorológicas (OpenWeather)"
        self._location_text = "São Paulo, BR"
        self._temp_text = "-- °C"
        self._feels_text = "-- °C"
        self._humidity_text = "-- %"
        self._pressure_text = "-- hPa"
        self._wind_text = "-- km/h"
        self._condition_text = "Aguardando dados..."

    @property
    def title_text(self) -> str:
        return self._title_text

    @property
    def location_text(self) -> str:
        return self._location_text

    @property
    def temp_text(self) -> str:
        return self._temp_text

    @property
    def feels_text(self) -> str:
        return self._feels_text

    @property
    def humidity_text(self) -> str:
        return self._humidity_text

    @property
    def pressure_text(self) -> str:
        return self._pressure_text

    @property
    def wind_text(self) -> str:
        return self._wind_text

    @property
    def condition_text(self) -> str:
        return self._condition_text

    def update_data(self, data: WeatherSnapshot | dict) -> None:
        """Atualiza o estado a partir dos dados do WeatherSnapshot."""
        if isinstance(data, WeatherSnapshot):
            self._location_text = data.location_name
            self._temp_text = f"{data.temperature_c:.1f} °C"
            self._feels_text = f"{data.feels_like_c:.1f} °C" if data.feels_like_c is not None else "--"
            self._humidity_text = f"{data.humidity_pct:.0f} %"
            self._pressure_text = f"{data.pressure_hpa:.0f} hPa"
            self._condition_text = data.condition.description.capitalize() if data.condition else "Limpo"
            if data.wind and data.wind.speed:
                self._wind_text = f"{data.wind.speed.in_kmh:.1f} km/h ({data.wind.direction_name})"
            else:
                self._wind_text = "-- km/h"
        elif isinstance(data, dict):
            self._location_text = data.get("location_name", "São Paulo, BR")
            self._temp_text = f"{data.get('temperature_c', 0):.1f} °C"
            self._feels_text = f"{data.get('feels_like_c', 0):.1f} °C"
            self._humidity_text = f"{data.get('humidity_pct', 0):.0f} %"
            self._pressure_text = f"{data.get('pressure_hpa', 1013):.0f} hPa"
            self._condition_text = data.get("condition", {}).get("description", "Normal").capitalize()
            self._wind_text = "-- km/h"

        self.data_changed.emit()
