"""
AeroTracker Core — Janela Principal Desktop (Airspace Companion UI)
===================================================================
Layout tripartite profissional com Sidebar de Navegação (Área 1),
Workspace Central (Área 2) e Simulador Device Digital Twin ESP32-S3 (Área 3).
"""

from typing import Any, Optional

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QMainWindow, QScrollArea, QStackedWidget, QVBoxLayout, QWidget

from display.assets.icons import SVGIcons
from display.components.device_preview_widget import DevicePreviewPanel
from display.components.primary_button import GlassButton
from display.desktop.screens.clock import ClockController, ClockModel, ClockView
from display.desktop.screens.dashboard import DashboardController, DashboardModel, DashboardView
from display.desktop.screens.iss import ISSController, ISSModel, ISSView
from display.desktop.screens.launches import LaunchesController, LaunchesModel, LaunchesView
from display.desktop.screens.moon import MoonController, MoonModel, MoonView
from display.desktop.screens.radar import RadarController, RadarModel, RadarView
from display.desktop.screens.settings import SettingsController, SettingsModel, SettingsView
from display.desktop.screens.solar_system import SolarSystemController, SolarSystemModel, SolarSystemView
from display.desktop.screens.tracker import TrackerController, TrackerModel, TrackerView
from display.desktop.screens.weather import WeatherController, WeatherModel, WeatherView
from display.desktop.screens.world_map import WorldMapController, WorldMapModel, WorldMapView
from display.theme import Theme
from utils.logger import get_logger

logger = get_logger(__name__)


class MainWindow(QMainWindow):
    """
    Janela principal com Layout Tripartite (Sidebar + Workspace + Device Digital Twin).
    """

    def __init__(self, services: Optional[dict[str, Any]] = None) -> None:
        super().__init__()
        self.services = services or {}

        self.setWindowTitle("AeroTracker Core — Airspace Instrument & Control Station")
        self.resize(1280, 800)
        self.setMinimumSize(1100, 700)
        self.setStyleSheet(Theme.Styles.app_stylesheet())

        # Central Widget & Main Horizontal Layout (3 Áreas)
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)

        self.main_layout = QHBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # =====================================================================
        # ÁREA 1: SIDEBAR (Esquerda)
        # =====================================================================
        self.sidebar_frame = QFrame(self)
        self.sidebar_frame.setFixedWidth(190)
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

        # Logo Reticular Radar AIRSPACE INSTRUMENT
        logo_box = QHBoxLayout()
        logo_icon = QLabel("🎯")
        logo_icon.setFont(Theme.Fonts.title_display())
        logo_icon.setStyleSheet(f"color: {Theme.Colors.PRIMARY}; border: none;")
        logo_text_box = QVBoxLayout()
        logo_text_box.setSpacing(0)

        lbl_logo_main = QLabel("Radar")
        lbl_logo_main.setFont(Theme.Fonts.title_section())
        lbl_logo_main.setStyleSheet(f"color: {Theme.Colors.TEXT_PRIMARY}; border: none;")

        lbl_logo_sub = QLabel("AIRSPACE INSTRUMENT")
        lbl_logo_sub.setFont(Theme.Fonts.caption())
        lbl_logo_sub.setStyleSheet(f"color: {Theme.Colors.TEXT_MUTED}; border: none; font-size: 7px; letter-spacing: 1px;")

        logo_text_box.addWidget(lbl_logo_main)
        logo_text_box.addWidget(lbl_logo_sub)
        logo_box.addWidget(logo_icon)
        logo_box.addLayout(logo_text_box)
        logo_box.addStretch()

        self.sidebar_layout.addLayout(logo_box)
        self.sidebar_layout.addSpacing(Theme.Dimensions.PAD_M)

        # Scrollable Menu
        self.side_scroll = QScrollArea()
        self.side_scroll.setWidgetResizable(True)
        self.side_content = QWidget()
        self.side_menu_layout = QVBoxLayout(self.side_content)
        self.side_menu_layout.setContentsMargins(0, 0, 0, 0)
        self.side_menu_layout.setSpacing(Theme.Dimensions.PAD_XS)
        self.side_scroll.setWidget(self.side_content)

        self.sidebar_layout.addWidget(self.side_scroll)

        self.sidebar_layout.addStretch()

        # Botões Circulares Utilitários (Chave 🔑 e Grid ⁝⁝)
        util_box = QHBoxLayout()
        util_box.setSpacing(Theme.Dimensions.PAD_S)
        btn_key = QLabel("🔑")
        btn_key.setStyleSheet(f"""
            background-color: {Theme.Colors.BG_CARD};
            color: {Theme.Colors.TEXT_MUTED};
            border: 1px solid {Theme.Colors.BORDER};
            border-radius: 15px;
            padding: 6px;
        """)
        btn_grid = QLabel("⁝⁝")
        btn_grid.setStyleSheet(f"""
            background-color: {Theme.Colors.BG_CARD};
            color: {Theme.Colors.TEXT_MUTED};
            border: 1px solid {Theme.Colors.BORDER};
            border-radius: 15px;
            padding: 6px;
        """)
        util_box.addWidget(btn_key)
        util_box.addWidget(btn_grid)
        util_box.addStretch()
        self.sidebar_layout.addLayout(util_box)
        self.sidebar_layout.addSpacing(Theme.Dimensions.PAD_S)

        # Rodapé da Sidebar: Status do Hardware ESP32-S3
        esp_badge = QFrame()
        esp_badge.setStyleSheet(f"""
            QFrame {{
                background-color: {Theme.Colors.BG_CARD};
                border: 1px solid {Theme.Colors.BORDER};
                border-radius: {Theme.Dimensions.RADIUS_M}px;
                padding: 6px;
            }}
        """)
        esp_layout = QVBoxLayout(esp_badge)
        esp_layout.setContentsMargins(Theme.Dimensions.PAD_XS, Theme.Dimensions.PAD_XS, Theme.Dimensions.PAD_XS, Theme.Dimensions.PAD_XS)

        l_esp1 = QLabel("🟢 ESP32-S3")
        l_esp1.setFont(Theme.Fonts.body_bold())
        l_esp1.setStyleSheet(f"color: {Theme.Colors.PRIMARY}; border: none; font-size: 10px;")
        l_esp2 = QLabel("466 × 466 AMOLED")
        l_esp2.setFont(Theme.Fonts.caption())
        l_esp2.setStyleSheet(f"color: {Theme.Colors.TEXT_MUTED}; border: none; font-size: 8px;")

        esp_layout.addWidget(l_esp1)
        esp_layout.addWidget(l_esp2)
        self.sidebar_layout.addWidget(esp_badge)

        self.main_layout.addWidget(self.sidebar_frame)

        # =====================================================================
        # ÁREA 2: WORKSPACE (Centro)
        # =====================================================================
        self.stack = QStackedWidget(self)
        self._init_screens()
        self.main_layout.addWidget(self.stack)

        # Seleciona a tela 'Tracker' (Index 1) como ativa por padrão
        self.stack.setCurrentIndex(1)

        # =====================================================================
        # ÁREA 3: DEVICE DIGITAL TWIN (Direita)
        # =====================================================================
        self.device_twin_panel = DevicePreviewPanel(self)
        self.main_layout.addWidget(self.device_twin_panel)

        # Conecta sinal de telemetria em tempo real do Tracker ao mostrador do ESP32
        self.tracker_m.data_changed.connect(
            lambda: self.device_twin_panel.circle_display.set_realtime_data(
                self.tracker_m.active_flight,
                self.tracker_m.dist_from_str,
                self.tracker_m.dist_to_str,
                self.tracker_m.progress_pct,
            )
        )

    def _init_screens(self) -> None:
        """Instancia os módulos e constrói o menu de navegação da Sidebar."""
        nav_items = [
            ("Radar", SVGIcons.RADAR),
            ("Tracker", SVGIcons.PLANE),
            ("Weather", SVGIcons.WEATHER),
            ("Clock", SVGIcons.CLOCK),
            ("Space", SVGIcons.ISS),
            ("Space Launches", SVGIcons.LAUNCH),
            ("Moon", SVGIcons.MOON),
            ("Solar System", SVGIcons.SOLAR_SYSTEM),
            ("Settings", SVGIcons.SETTINGS),
        ]

        # 0. Radar
        radar_m = RadarModel()
        self.radar_c = RadarController(radar_m, service=self.services.get("aircraft"))
        r_view = RadarView(radar_m)
        r_view.refresh_requested.connect(self.radar_c.trigger_manual_update)
        self.stack.addWidget(r_view)

        # 1. Tracker (Voo em tempo real Airspace Companion)
        self.tracker_m = TrackerModel()
        self.tracker_c = TrackerController(self.tracker_m, service=self.services.get("aircraft"))
        self.stack.addWidget(TrackerView(self.tracker_m))

        # 2. Weather
        wx_m = WeatherModel()
        self.wx_c = WeatherController(wx_m, service=self.services.get("weather"))
        w_view = WeatherView(wx_m)
        w_view.refresh_requested.connect(self.wx_c.trigger_manual_update)
        self.stack.addWidget(w_view)

        # 3. Clock
        clk_m = ClockModel()
        self.clk_c = ClockController(clk_m)
        self.stack.addWidget(ClockView(clk_m))

        # 4. Space / ISS
        iss_m = ISSModel()
        self.iss_c = ISSController(iss_m, service=self.services.get("iss"))
        i_view = ISSView(iss_m)
        i_view.refresh_requested.connect(self.iss_c.trigger_manual_update)
        self.stack.addWidget(i_view)

        # 5. Space Launches
        launch_m = LaunchesModel()
        self.launch_c = LaunchesController(launch_m, service=self.services.get("launch"))
        l_view = LaunchesView(launch_m)
        l_view.refresh_requested.connect(self.launch_c.trigger_manual_update)
        self.stack.addWidget(l_view)

        # 6. Moon
        moon_m = MoonModel()
        self.moon_c = MoonController(moon_m)
        self.stack.addWidget(MoonView(moon_m))

        # 7. Solar System
        ss_m = SolarSystemModel()
        self.ss_c = SolarSystemController(ss_m)
        self.stack.addWidget(SolarSystemView(ss_m))

        # 8. Settings
        set_m = SettingsModel()
        self.set_c = SettingsController(set_m)
        self.stack.addWidget(SettingsView(set_m))

        # Adiciona os botões pílula de navegação na Sidebar
        self.nav_buttons = []
        for idx, (label, svg) in enumerate(nav_items):
            btn = GlassButton(label, is_primary=(idx == 1))
            btn.setIcon(SVGIcons.get_icon(svg, color=Theme.Colors.PRIMARY if idx == 1 else Theme.Colors.TEXT_MUTED))
            btn.clicked.connect(lambda checked=False, i=idx: self._select_nav(i))
            self.side_menu_layout.addWidget(btn)
            self.nav_buttons.append(btn)

        self.side_menu_layout.addStretch()
        self._select_nav(1)

    def _select_nav(self, index: int) -> None:
        """Altera a tela ativa no QStackedWidget e atualiza o estilo dos botões."""
        self.stack.setCurrentIndex(index)
        for i, btn in enumerate(self.nav_buttons):
            if i == index:
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {Theme.Colors.POSITIVE_BG};
                        color: {Theme.Colors.TEXT_PRIMARY};
                        border: 1px solid {Theme.Colors.PRIMARY};
                        border-radius: {Theme.Dimensions.RADIUS_PILL}px;
                        padding: 8px 14px;
                        font-size: 11px;
                        font-weight: bold;
                        text-align: left;
                    }}
                """)
            else:
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: transparent;
                        color: {Theme.Colors.TEXT_SECONDARY};
                        border: 1px solid transparent;
                        border-radius: {Theme.Dimensions.RADIUS_PILL}px;
                        padding: 8px 14px;
                        font-size: 11px;
                        text-align: left;
                    }}
                    QPushButton:hover {{
                        background-color: {Theme.Colors.BG_CARD};
                        color: {Theme.Colors.TEXT_PRIMARY};
                    }}
                """)
