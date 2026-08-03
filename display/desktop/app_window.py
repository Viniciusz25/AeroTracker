"""
AeroTracker Core — Janela Principal Desktop (PySide6 / Qt)
===========================================================
Orquestra as telas MVC utilizando QMainWindow, QStackedWidget e barra lateral.
"""

from typing import Any, Optional

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QMainWindow, QPushButton, QStackedWidget, QVBoxLayout, QWidget

from display.assets.icons import SVGIcons
from display.components.primary_button import AnimatedButton
from display.desktop.screens.aircraft import AircraftController, AircraftModel, AircraftView
from display.desktop.screens.dashboard import DashboardController, DashboardModel, DashboardView
from display.desktop.screens.weather import WeatherController, WeatherModel, WeatherView
from display.theme import Theme
from utils.logger import get_logger

logger = get_logger(__name__)


class MainWindow(QMainWindow):
    """
    Janela principal Desktop construída com PySide6 e componentes do Design System.
    """

    def __init__(self, services: Optional[dict[str, Any]] = None) -> None:
        super().__init__()
        self.services = services or {}

        self.setWindowTitle("AeroTracker Core — Estação de Monitoramento Aeroespacial")
        self.resize(1150, 700)
        self.setMinimumSize(950, 600)
        self.setStyleSheet(Theme.Styles.app_stylesheet())

        # Widget Central e Layout Principal (Sidebar + Screen Stack)
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)

        self.main_layout = QHBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # ---------------------------------------------------------------------
        # Menu Lateral (Sidebar)
        # ---------------------------------------------------------------------
        self.sidebar_frame = QFrame(self)
        self.sidebar_frame.setFixedWidth(220)
        self.sidebar_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {Theme.Colors.BG_SIDEBAR};
                border-right: 1px solid {Theme.Colors.BORDER};
            }}
        """)
        self.sidebar_layout = QVBoxLayout(self.sidebar_frame)
        self.sidebar_layout.setContentsMargins(
            Theme.Dimensions.PAD_M,
            Theme.Dimensions.PAD_L,
            Theme.Dimensions.PAD_M,
            Theme.Dimensions.PAD_L,
        )
        self.sidebar_layout.setSpacing(Theme.Dimensions.PAD_S)

        # Logo da Aplicação com Ícone SVG
        self.lbl_logo = QLabel("✈ AeroTracker")
        self.lbl_logo.setFont(Theme.Fonts.title_main())
        self.lbl_logo.setStyleSheet(f"color: {Theme.Colors.PRIMARY}; border: none;")
        self.sidebar_layout.addWidget(self.lbl_logo)
        self.sidebar_layout.addSpacing(Theme.Dimensions.PAD_L)

        # Botões de Navegação com Ícones SVG e Animação
        self.btn_dash = AnimatedButton(" Dashboard", is_primary=False)
        self.btn_dash.setIcon(SVGIcons.get_icon(SVGIcons.DASHBOARD, color=Theme.Colors.TEXT_PRIMARY))
        self.btn_dash.clicked.connect(lambda: self.stack.setCurrentIndex(0))
        self.sidebar_layout.addWidget(self.btn_dash)

        self.btn_aircraft = AnimatedButton(" Radar Aeronaves", is_primary=False)
        self.btn_aircraft.setIcon(SVGIcons.get_icon(SVGIcons.PLANE, color=Theme.Colors.TEXT_PRIMARY))
        self.btn_aircraft.clicked.connect(lambda: self.stack.setCurrentIndex(1))
        self.sidebar_layout.addWidget(self.btn_aircraft)

        self.btn_weather = AnimatedButton(" Clima", is_primary=False)
        self.btn_weather.setIcon(SVGIcons.get_icon(SVGIcons.WEATHER, color=Theme.Colors.TEXT_PRIMARY))
        self.btn_weather.clicked.connect(lambda: self.stack.setCurrentIndex(2))
        self.sidebar_layout.addWidget(self.btn_weather)

        self.sidebar_layout.addStretch()
        self.main_layout.addWidget(self.sidebar_frame)

        # ---------------------------------------------------------------------
        # QStackedWidget para Alternância de Telas MVC
        # ---------------------------------------------------------------------
        self.stack = QStackedWidget(self)

        # 1. Dashboard (MVC)
        self.dash_model = DashboardModel()
        self.dash_controller = DashboardController(self.dash_model)
        self.dash_view = DashboardView(self.dash_model)
        self.stack.addWidget(self.dash_view)

        # 2. Radar de Aeronaves (MVC)
        self.ac_model = AircraftModel()
        self.ac_controller = AircraftController(self.ac_model, service=self.services.get("aircraft"))
        self.ac_view = AircraftView(self.ac_model)
        self.ac_view.refresh_requested.connect(self.ac_controller.trigger_manual_update)
        self.stack.addWidget(self.ac_view)

        # 3. Clima (MVC)
        self.wx_model = WeatherModel()
        self.wx_controller = WeatherController(self.wx_model, service=self.services.get("weather"))
        self.wx_view = WeatherView(self.wx_model)
        self.wx_view.refresh_requested.connect(self.wx_controller.trigger_manual_update)
        self.stack.addWidget(self.wx_view)

        self.main_layout.addWidget(self.stack)
