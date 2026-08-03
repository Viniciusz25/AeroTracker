"""
AeroTracker Core — Janela Principal Desktop (Glass Cockpit Engine)
==================================================================
Orquestra as 11 telas independentes MVC utilizando QMainWindow, QStackedWidget
e painel de instrumentos no estilo Glass Cockpit / NASA Mission Control.
"""

from typing import Any, Optional

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QMainWindow, QScrollArea, QStackedWidget, QVBoxLayout, QWidget

from display.assets.icons import SVGIcons
from display.components.primary_button import GlassButton
from display.desktop.screens.aircraft_details import AircraftDetailsController, AircraftDetailsModel, AircraftDetailsView
from display.desktop.screens.clock import ClockController, ClockModel, ClockView
from display.desktop.screens.dashboard import DashboardController, DashboardModel, DashboardView
from display.desktop.screens.iss import ISSController, ISSModel, ISSView
from display.desktop.screens.launches import LaunchesController, LaunchesModel, LaunchesView
from display.desktop.screens.moon import MoonController, MoonModel, MoonView
from display.desktop.screens.radar import RadarController, RadarModel, RadarView
from display.desktop.screens.settings import SettingsController, SettingsModel, SettingsView
from display.desktop.screens.solar_system import SolarSystemController, SolarSystemModel, SolarSystemView
from display.desktop.screens.weather import WeatherController, WeatherModel, WeatherView
from display.desktop.screens.world_map import WorldMapController, WorldMapModel, WorldMapView
from display.theme import Theme
from utils.logger import get_logger

logger = get_logger(__name__)


class MainWindow(QMainWindow):
    """
    Janela principal com os 11 módulos independentes Glass Cockpit.
    """

    def __init__(self, services: Optional[dict[str, Any]] = None) -> None:
        super().__init__()
        self.services = services or {}

        self.setWindowTitle("AeroTracker Core — Avionics Glass Cockpit & Control Station")
        self.resize(1200, 750)
        self.setMinimumSize(1000, 650)
        self.setStyleSheet(Theme.Styles.app_stylesheet())

        # Central Layout
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)

        self.main_layout = QHBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # ---------------------------------------------------------------------
        # Sidebar com as 11 Telas Independentes
        # ---------------------------------------------------------------------
        self.sidebar_frame = QFrame(self)
        self.sidebar_frame.setFixedWidth(210)
        self.sidebar_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {Theme.Colors.BG_SIDEBAR};
                border-right: 1px solid {Theme.Colors.BORDER};
            }}
        """)
        self.sidebar_layout = QVBoxLayout(self.sidebar_frame)
        self.sidebar_layout.setContentsMargins(
            Theme.Dimensions.PAD_S,
            Theme.Dimensions.PAD_M,
            Theme.Dimensions.PAD_S,
            Theme.Dimensions.PAD_M,
        )
        self.sidebar_layout.setSpacing(Theme.Dimensions.PAD_XS)

        # Logo Glass Cockpit
        self.lbl_logo = QLabel("✈ AEROTRACKER")
        self.lbl_logo.setFont(Theme.Fonts.title_display())
        self.lbl_logo.setStyleSheet(f"color: {Theme.Colors.CYAN_NEON}; border: none;")
        self.sidebar_layout.addWidget(self.lbl_logo)
        self.sidebar_layout.addSpacing(Theme.Dimensions.PAD_S)

        # Scrollable Sidebar Menu
        self.side_scroll = QScrollArea()
        self.side_scroll.setWidgetResizable(True)
        self.side_content = QWidget()
        self.side_menu_layout = QVBoxLayout(self.side_content)
        self.side_menu_layout.setContentsMargins(0, 0, 0, 0)
        self.side_menu_layout.setSpacing(Theme.Dimensions.PAD_XS)
        self.side_scroll.setWidget(self.side_content)

        self.sidebar_layout.addWidget(self.side_scroll)
        self.main_layout.addWidget(self.sidebar_frame)

        # Stack de Telas
        self.stack = QStackedWidget(self)

        # Instanciação dos 11 Tripletos MVC Independentes
        self._init_screens()

        self.main_layout.addWidget(self.stack)

    def _init_screens(self) -> None:
        """Inicializa e registra os 11 componentes independentes."""
        nav_items = [
            (" Dashboard", SVGIcons.DASHBOARD),
            (" Radar ATC", SVGIcons.RADAR),
            (" World Map", SVGIcons.WORLD_MAP),
            (" Weather", SVGIcons.WEATHER),
            (" ISS Tracker", SVGIcons.ISS),
            (" Moon Phase", SVGIcons.MOON),
            (" Solar System", SVGIcons.SOLAR_SYSTEM),
            (" Launches", SVGIcons.LAUNCH),
            (" Target Details", SVGIcons.DETAILS),
            (" Settings", SVGIcons.SETTINGS),
            (" UTC Chrono", SVGIcons.CLOCK),
        ]

        # 1. Dashboard
        dash_m = DashboardModel()
        self.dash_c = DashboardController(dash_m)
        self.stack.addWidget(DashboardView(dash_m))

        # 2. Radar
        radar_m = RadarModel()
        self.radar_c = RadarController(radar_m, service=self.services.get("aircraft"))
        r_view = RadarView(radar_m)
        r_view.refresh_requested.connect(self.radar_c.trigger_manual_update)
        self.stack.addWidget(r_view)

        # 3. World Map
        world_m = WorldMapModel()
        self.world_c = WorldMapController(world_m)
        self.stack.addWidget(WorldMapView(world_m))

        # 4. Weather
        wx_m = WeatherModel()
        self.wx_c = WeatherController(wx_m, service=self.services.get("weather"))
        w_view = WeatherView(wx_m)
        w_view.refresh_requested.connect(self.wx_c.trigger_manual_update)
        self.stack.addWidget(w_view)

        # 5. ISS
        iss_m = ISSModel()
        self.iss_c = ISSController(iss_m, service=self.services.get("iss"))
        i_view = ISSView(iss_m)
        i_view.refresh_requested.connect(self.iss_c.trigger_manual_update)
        self.stack.addWidget(i_view)

        # 6. Moon
        moon_m = MoonModel()
        self.moon_c = MoonController(moon_m)
        self.stack.addWidget(MoonView(moon_m))

        # 7. Solar System
        ss_m = SolarSystemModel()
        self.ss_c = SolarSystemController(ss_m)
        self.stack.addWidget(SolarSystemView(ss_m))

        # 8. Launches
        launch_m = LaunchesModel()
        self.launch_c = LaunchesController(launch_m, service=self.services.get("launch"))
        l_view = LaunchesView(launch_m)
        l_view.refresh_requested.connect(self.launch_c.trigger_manual_update)
        self.stack.addWidget(l_view)

        # 9. Details
        det_m = AircraftDetailsModel()
        self.det_c = AircraftDetailsController(det_m)
        self.stack.addWidget(AircraftDetailsView(det_m))

        # 10. Settings
        set_m = SettingsModel()
        self.set_c = SettingsController(set_m)
        self.stack.addWidget(SettingsView(set_m))

        # 11. Clock
        clk_m = ClockModel()
        self.clk_c = ClockController(clk_m)
        self.stack.addWidget(ClockView(clk_m))

        # Adiciona botões de navegação na Sidebar
        for idx, (label, svg) in enumerate(nav_items):
            btn = GlassButton(label, is_primary=False)
            btn.setIcon(SVGIcons.get_icon(svg, color=Theme.Colors.CYAN_NEON))
            btn.clicked.connect(lambda checked=False, i=idx: self.stack.setCurrentIndex(i))
            self.side_menu_layout.addWidget(btn)

        self.side_menu_layout.addStretch()
