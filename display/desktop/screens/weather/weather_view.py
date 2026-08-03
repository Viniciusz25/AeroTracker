"""
AeroTracker Core — Weather View (MVC)
=====================================
View pura da tela de Clima baseada em layouts dinâmicos e componentes reutilizáveis.
"""

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QGridLayout, QHBoxLayout, QLabel, QVBoxLayout, QWidget

from display.components.animated_card import GlassPanel
from display.components.primary_button import GlassButton
from display.components.status_badge import AvionicsBadge
from display.desktop.screens.weather.weather_model import WeatherModel
from display.desktop.screens.weather.weather_widgets import WeatherMetricCardWidget
from display.theme import Theme


class WeatherView(QWidget):
    """
    View pura do módulo de clima tático.
    """

    refresh_requested = Signal()

    def __init__(self, model: WeatherModel, parent=None) -> None:
        super().__init__(parent)
        self.model = model

        # Layout Principal
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(
            Theme.Dimensions.PAD_L,
            Theme.Dimensions.PAD_L,
            Theme.Dimensions.PAD_L,
            Theme.Dimensions.PAD_L,
        )
        self.main_layout.setSpacing(Theme.Dimensions.PAD_M)

        # Header Bar
        header_layout = QHBoxLayout()
        self.lbl_title = QLabel(self.model.title_text)
        self.lbl_title.setFont(Theme.Fonts.title_display())
        self.lbl_title.setStyleSheet(f"color: {Theme.Colors.TEXT_PRIMARY};")
        header_layout.addWidget(self.lbl_title)
        header_layout.addStretch()

        self.btn_refresh = GlassButton("🔄 SCAN METAR", is_primary=True)
        self.btn_refresh.clicked.connect(self.refresh_requested.emit)
        header_layout.addWidget(self.btn_refresh)
        self.main_layout.addLayout(header_layout)

        # Main Card de Destaque Temperatura
        self.card_main = GlassPanel()

        top_row = QHBoxLayout()
        self.lbl_location = QLabel(f"📍 {self.model.location_text}")
        self.lbl_location.setFont(Theme.Fonts.title_section())
        self.lbl_location.setStyleSheet(f"color: {Theme.Colors.TEXT_PRIMARY}; border: none;")
        top_row.addWidget(self.lbl_location)
        top_row.addStretch()

        self.vfr_badge = AvionicsBadge("VFR OPTIMAL", badge_type="positive")
        top_row.addWidget(self.vfr_badge)
        self.card_main.main_layout.addLayout(top_row)

        self.lbl_temp = QLabel(self.model.temp_text)
        self.lbl_temp.setFont(Theme.Fonts.metric_huge())
        self.lbl_temp.setStyleSheet(f"color: {Theme.Colors.PRIMARY}; border: none;")
        self.card_main.main_layout.addWidget(self.lbl_temp)

        self.lbl_cond = QLabel(f"Condição: {self.model.condition_text}")
        self.lbl_cond.setFont(Theme.Fonts.body_bold())
        self.lbl_cond.setStyleSheet(f"color: {Theme.Colors.TEXT_SECONDARY}; border: none;")
        self.card_main.main_layout.addWidget(self.lbl_cond)

        self.main_layout.addWidget(self.card_main)

        # Grid de Métricas Secundárias
        self.grid_layout = QGridLayout()
        self.grid_layout.setSpacing(Theme.Dimensions.PAD_M)

        self.card_feels = WeatherMetricCardWidget("🌡 Sensação Térmica", self.model.feels_text)
        self.card_humidity = WeatherMetricCardWidget("💧 Umidade Relativa", self.model.humidity_text)
        self.card_wind = WeatherMetricCardWidget("💨 Vento Tático", self.model.wind_text)
        self.card_pressure = WeatherMetricCardWidget("⏲ Pressão Atmosférica", self.model.pressure_text)

        self.grid_layout.addWidget(self.card_feels, 0, 0)
        self.grid_layout.addWidget(self.card_humidity, 0, 1)
        self.grid_layout.addWidget(self.card_wind, 1, 0)
        self.grid_layout.addWidget(self.card_pressure, 1, 1)

        self.main_layout.addLayout(self.grid_layout)
        self.main_layout.addStretch()

        # Vincula atualização ao sinal do Model
        self.model.data_changed.connect(self.update_from_model)

    def update_from_model(self) -> None:
        """Atualiza os valores da View."""
        self.lbl_location.setText(f"📍 {self.model.location_text}")
        self.lbl_temp.setText(self.model.temp_text)
        self.lbl_cond.setText(f"Condição: {self.model.condition_text}")

        self.card_feels.set_value(self.model.feels_text)
        self.card_humidity.set_value(self.model.humidity_text)
        self.card_wind.set_value(self.model.wind_text)
        self.card_pressure.set_value(self.model.pressure_text)
