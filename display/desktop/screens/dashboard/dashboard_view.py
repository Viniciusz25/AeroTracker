"""
AeroTracker Core — Dashboard View
==================================
Interface pura da tela de Dashboard. Não possui lógica de dados ou consumo de APIs.
Todos os textos exibidos derivam do DashboardModel.
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QGridLayout, QLabel, QVBoxLayout, QWidget
from display.desktop.screens.dashboard.dashboard_model import DashboardModel
from display.desktop.screens.dashboard.dashboard_widgets import MetricCardWidget
from display.theme import Theme


class DashboardView(QWidget):
    """
    View pura do Dashboard construída com layouts dinâmicos e componentes reutilizáveis.
    """

    def __init__(self, model: DashboardModel, parent=None) -> None:
        super().__init__(parent)
        self.model = model

        # Layout Principal
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(
            Theme.Dimensions.PAD_L,
            Theme.Dimensions.PAD_L,
            Theme.Dimensions.PAD_L,
            Theme.Dimensions.PAD_L,
        )
        self.layout.setSpacing(Theme.Dimensions.PAD_M)

        # Header: Título e Subtítulo (Textos vindos do Model)
        self.lbl_title = QLabel(self.model.title_text)
        self.lbl_title.setFont(Theme.Fonts.title_main())
        self.lbl_title.setStyleSheet(f"color: {Theme.Colors.TEXT_PRIMARY};")
        self.layout.addWidget(self.lbl_title)

        self.lbl_subtitle = QLabel(self.model.subtitle_text)
        self.lbl_subtitle.setFont(Theme.Fonts.body())
        self.lbl_subtitle.setStyleSheet(f"color: {Theme.Colors.TEXT_SECONDARY};")
        self.layout.addWidget(self.lbl_subtitle)

        # Grid 2x2 para Cards de Métricas
        self.grid_layout = QGridLayout()
        self.grid_layout.setSpacing(Theme.Dimensions.PAD_M)

        self.card_modules = MetricCardWidget("📦 Módulos Ativos", self.model.active_modules_text, Theme.Colors.PRIMARY)
        self.card_location = MetricCardWidget("📍 Localização Base", self.model.location_text, Theme.Colors.AIRBORNE)
        self.card_aircraft = MetricCardWidget("✈️ Radar de Aeronaves", self.model.aircraft_count_text, Theme.Colors.ON_GROUND)
        self.card_weather = MetricCardWidget("🌤 Clima Local", self.model.weather_temp_text, Theme.Colors.PRIMARY)

        self.grid_layout.addWidget(self.card_modules, 0, 0)
        self.grid_layout.addWidget(self.card_location, 0, 1)
        self.grid_layout.addWidget(self.card_aircraft, 1, 0)
        self.grid_layout.addWidget(self.card_weather, 1, 1)

        self.layout.addLayout(self.grid_layout)
        self.layout.addStretch()

        # Conecta sinal do Model para atualização reativa
        self.model.data_changed.connect(self.update_from_model)

    def update_from_model(self) -> None:
        """Atualiza a View reativamente com os dados do Model."""
        self.card_modules.set_value(self.model.active_modules_text, Theme.Colors.PRIMARY)
        self.card_location.set_value(self.model.location_text, Theme.Colors.AIRBORNE)
        self.card_aircraft.set_value(self.model.aircraft_count_text, Theme.Colors.PRIMARY)
        self.card_weather.set_value(self.model.weather_temp_text, Theme.Colors.AIRBORNE)
