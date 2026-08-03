"""
AeroTracker Core — Dashboard Model
===================================
Gerencia o estado e dados exibidos no Dashboard.
Todos os textos e métricas exibidos na View derivam deste Model.
"""

from PySide6.QtCore import QObject, Signal


class DashboardModel(QObject):
    """
    Model da tela de Dashboard.
    Emite sinal data_changed quando os dados são atualizados.
    """

    data_changed = Signal()

    def __init__(self) -> None:
        super().__init__()
        self._title_text = "✈ AeroTracker Core — Dashboard"
        self._subtitle_text = "Plataforma Integrada de Monitoramento Aeroespacial"
        self._active_modules_text = "5 / 5"
        self._location_text = "São Paulo, BR (-23.55, -46.63)"
        self._aircraft_count_text = "Buscando dados..."
        self._weather_temp_text = "Buscando dados..."

    # Getters de texto para a View
    @property
    def title_text(self) -> str:
        return self._title_text

    @property
    def subtitle_text(self) -> str:
        return self._subtitle_text

    @property
    def active_modules_text(self) -> str:
        return self._active_modules_text

    @property
    def location_text(self) -> str:
        return self._location_text

    @property
    def aircraft_count_text(self) -> str:
        return self._aircraft_count_text

    @property
    def weather_temp_text(self) -> str:
        return self._weather_temp_text

    # Setters que disparam sinal de atualização da View
    def update_aircraft_count(self, count: int) -> None:
        self._aircraft_count_text = f"{count} Aeronaves Detectadas"
        self.data_changed.emit()

    def update_weather_temp(self, temp: float, condition: str) -> None:
        self._weather_temp_text = f"{temp:.1f} °C — {condition.capitalize()}"
        self.data_changed.emit()

    def update_modules_status(self, active: int, total: int) -> None:
        self._active_modules_text = f"{active} / {total}"
        self.data_changed.emit()
