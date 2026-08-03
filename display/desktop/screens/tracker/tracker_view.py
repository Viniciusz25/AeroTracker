"""
AeroTracker Core — Tracker View (MVC)
=====================================
View pura do módulo Tracker (Airspace Companion UI com animação em tempo real).
"""

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QLineEdit, QProgressBar, QVBoxLayout, QWidget

from display.components.animated_card import GlassPanel
from display.components.primary_button import GlassButton
from display.desktop.screens.tracker.tracker_model import TrackerModel
from display.theme import Theme


class TrackerView(QWidget):
    """
    View pura do módulo Tracker (Airspace Companion UI).
    """

    add_flight_requested = Signal(str, str)

    def __init__(self, model: TrackerModel, parent=None) -> None:
        super().__init__(parent)
        self.model = model

        layout = QVBoxLayout(self)
        layout.setContentsMargins(
            Theme.Dimensions.PAD_L,
            Theme.Dimensions.PAD_L,
            Theme.Dimensions.PAD_L,
            Theme.Dimensions.PAD_L,
        )
        layout.setSpacing(Theme.Dimensions.PAD_M)

        # 1. Header Bar: Título, Subtítulo e Botão Sync Flight
        header_row = QHBoxLayout()
        h_title_box = QVBoxLayout()
        h_title_box.setSpacing(2)

        self.lbl_title = QLabel(self.model.title_text)
        self.lbl_title.setFont(Theme.Fonts.title_display())
        self.lbl_title.setStyleSheet(f"color: {Theme.Colors.TEXT_PRIMARY};")
        h_title_box.addWidget(self.lbl_title)

        self.lbl_subtitle = QLabel(self.model.subtitle_text)
        self.lbl_subtitle.setFont(Theme.Fonts.caption())
        self.lbl_subtitle.setStyleSheet(f"color: {Theme.Colors.TEXT_MUTED};")
        h_title_box.addWidget(self.lbl_subtitle)

        header_row.addLayout(h_title_box)
        header_row.addStretch()

        self.btn_sync = GlassButton("⚙ Sync Flight", is_primary=False)
        self.btn_sync.setStyleSheet(f"""
            QPushButton {{
                background-color: {Theme.Colors.BG_CARD};
                color: {Theme.Colors.TEXT_PRIMARY};
                border: 1px solid {Theme.Colors.BORDER};
                border-radius: {Theme.Dimensions.RADIUS_S}px;
                padding: 6px 14px;
                font-size: 11px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {Theme.Colors.BG_CARD_HOVER};
                border: 1px solid {Theme.Colors.PRIMARY};
            }}
        """)
        header_row.addWidget(self.btn_sync)
        layout.addLayout(header_row)

        # 2. Card 1: FLIGHT TO TRACK
        c1 = GlassPanel()
        c1.main_layout.setSpacing(Theme.Dimensions.PAD_S)

        l_c1_title = QLabel("✈  FLIGHT TO TRACK")
        l_c1_title.setFont(Theme.Fonts.caption())
        l_c1_title.setStyleSheet(f"color: {Theme.Colors.TEXT_MUTED}; border: none; font-weight: bold; letter-spacing: 1px;")
        c1.main_layout.addWidget(l_c1_title)

        form_row = QHBoxLayout()
        form_row.setSpacing(Theme.Dimensions.PAD_M)

        f_box = QVBoxLayout()
        f_box.setSpacing(4)
        f_lbl = QLabel("Flight number")
        f_lbl.setFont(Theme.Fonts.caption())
        f_lbl.setStyleSheet(f"color: {Theme.Colors.TEXT_SECONDARY}; border: none;")
        self.input_flight = QLineEdit(self.model.active_flight)
        self.input_flight.setFixedWidth(160)
        f_box.addWidget(f_lbl)
        f_box.addWidget(self.input_flight)

        d_box = QVBoxLayout()
        d_box.setSpacing(4)
        d_lbl = QLabel("Departure date")
        d_lbl.setFont(Theme.Fonts.caption())
        d_lbl.setStyleSheet(f"color: {Theme.Colors.TEXT_SECONDARY}; border: none;")
        self.input_date = QLineEdit(self.model.departure_date)
        self.input_date.setFixedWidth(140)
        d_box.addWidget(d_lbl)
        d_box.addWidget(self.input_date)

        form_row.addLayout(f_box)
        form_row.addLayout(d_box)
        form_row.addStretch()

        btn_box = QHBoxLayout()
        btn_box.setSpacing(Theme.Dimensions.PAD_S)
        self.btn_add = GlassButton("Add Flight", is_primary=True)
        self.btn_add.setStyleSheet(f"""
            QPushButton {{
                background-color: #2A2F38;
                color: {Theme.Colors.TEXT_PRIMARY};
                border: 1px solid #363C47;
                border-radius: {Theme.Dimensions.RADIUS_S}px;
                padding: 7px 16px;
                font-size: 11px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #363C47;
                color: {Theme.Colors.PRIMARY};
            }}
        """)
        self.btn_add.clicked.connect(self._on_add_clicked)

        self.btn_refresh = GlassButton("Refresh Active", is_primary=False)
        self.btn_refresh.setStyleSheet(f"""
            QPushButton {{
                background-color: {Theme.Colors.BG_CARD};
                color: {Theme.Colors.TEXT_PRIMARY};
                border: 1px solid {Theme.Colors.BORDER};
                border-radius: {Theme.Dimensions.RADIUS_S}px;
                padding: 7px 16px;
                font-size: 11px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {Theme.Colors.BG_CARD_HOVER};
                border: 1px solid {Theme.Colors.PRIMARY};
            }}
        """)
        self.btn_refresh.clicked.connect(self._on_add_clicked)

        btn_box.addWidget(self.btn_add)
        btn_box.addWidget(self.btn_refresh)
        form_row.addLayout(btn_box)

        c1.main_layout.addLayout(form_row)

        l_c1_desc = QLabel(
            "Add as many future flights as you need. The earliest upcoming flight is prepared automatically; "
            "if two are underway at once, the later departure takes priority."
        )
        l_c1_desc.setFont(Theme.Fonts.caption())
        l_c1_desc.setWordWrap(True)
        l_c1_desc.setStyleSheet(f"color: {Theme.Colors.TEXT_MUTED}; border: none;")
        c1.main_layout.addWidget(l_c1_desc)

        layout.addWidget(c1)

        # 3. Card 2: FLIGHT SCHEDULE
        c2 = GlassPanel()
        c2.main_layout.setSpacing(Theme.Dimensions.PAD_S)

        l_c2_title = QLabel("🛫  FLIGHT SCHEDULE")
        l_c2_title.setFont(Theme.Fonts.caption())
        l_c2_title.setStyleSheet(f"color: {Theme.Colors.TEXT_MUTED}; border: none; font-weight: bold; letter-spacing: 1px;")
        c2.main_layout.addWidget(l_c2_title)

        sched_row = QHBoxLayout()
        sched_row.setSpacing(Theme.Dimensions.PAD_M)

        icon_plane = QLabel("✈")
        icon_plane.setFont(Theme.Fonts.body_bold())
        icon_plane.setStyleSheet(f"""
            color: {Theme.Colors.PRIMARY};
            background-color: {Theme.Colors.POSITIVE_BG};
            border: 1px solid {Theme.Colors.PRIMARY};
            border-radius: 14px;
            padding: 6px 10px;
        """)
        sched_row.addWidget(icon_plane)

        fn_box = QVBoxLayout()
        fn_box.setSpacing(2)
        self.l_fn = QLabel(f"{self.model.active_flight}  ACTIVE")
        self.l_fn.setFont(Theme.Fonts.body_bold())
        self.l_fn.setStyleSheet(f"color: {Theme.Colors.PRIMARY}; border: none;")
        self.l_date = QLabel("Sat, Aug 1, 2026")
        self.l_date.setFont(Theme.Fonts.caption())
        self.l_date.setStyleSheet(f"color: {Theme.Colors.TEXT_MUTED}; border: none;")
        fn_box.addWidget(self.l_fn)
        fn_box.addWidget(self.l_date)
        sched_row.addLayout(fn_box)

        sched_row.addStretch()

        info_box = QVBoxLayout()
        info_box.setSpacing(2)
        self.l_info1 = QLabel(f"{self.model.status_str} · ETA {self.model.eta}")
        self.l_info1.setFont(Theme.Fonts.caption())
        self.l_info1.setStyleSheet(f"color: {Theme.Colors.TEXT_SECONDARY}; border: none;")
        l_info2 = QLabel("Scheduled 02:00")
        l_info2.setFont(Theme.Fonts.caption())
        l_info2.setStyleSheet(f"color: {Theme.Colors.TEXT_MUTED}; border: none;")
        info_box.addWidget(self.l_info1)
        info_box.addWidget(l_info2)
        sched_row.addLayout(info_box)

        act_box = QHBoxLayout()
        act_box.setSpacing(Theme.Dimensions.PAD_S)
        btn_rel = QLabel("🔄")
        btn_rel.setStyleSheet(f"color: {Theme.Colors.TEXT_MUTED}; border: none; font-size: 12px;")
        btn_del = QLabel("🗑")
        btn_del.setStyleSheet(f"color: {Theme.Colors.TEXT_MUTED}; border: none; font-size: 12px;")
        act_box.addWidget(btn_rel)
        act_box.addWidget(btn_del)
        sched_row.addLayout(act_box)

        c2.main_layout.addLayout(sched_row)
        layout.addWidget(c2)

        # 4. Card 3: MAIN ROUTE DISPLAY (ICN -> SFO)
        c3 = GlassPanel()
        c3.main_layout.setSpacing(Theme.Dimensions.PAD_M)

        route_row = QHBoxLayout()

        # Origin
        orig_box = QVBoxLayout()
        orig_box.setSpacing(2)
        l_orig_code = QLabel(self.model.origin_code)
        l_orig_code.setFont(Theme.Fonts.metric_huge())
        l_orig_code.setStyleSheet(f"color: {Theme.Colors.TEXT_PRIMARY}; border: none;")
        l_orig_city = QLabel(self.model.origin_city)
        l_orig_city.setFont(Theme.Fonts.caption())
        l_orig_city.setStyleSheet(f"color: {Theme.Colors.TEXT_MUTED}; border: none;")
        orig_box.addWidget(l_orig_code)
        orig_box.addWidget(l_orig_city)
        route_row.addLayout(orig_box)

        route_row.addStretch()

        # Center Plane Icon
        center_box = QVBoxLayout()
        center_box.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.l_center_plane = QLabel(f"✈  {self.model.active_flight}")
        self.l_center_plane.setFont(Theme.Fonts.body_bold())
        self.l_center_plane.setStyleSheet(f"color: {Theme.Colors.PRIMARY}; border: none; font-size: 14px;")
        center_box.addWidget(self.l_center_plane)
        route_row.addLayout(center_box)

        route_row.addStretch()

        # Destination
        dest_box = QVBoxLayout()
        dest_box.setSpacing(2)
        dest_box.setAlignment(Qt.AlignmentFlag.AlignRight)
        l_dest_code = QLabel(self.model.dest_code)
        l_dest_code.setFont(Theme.Fonts.metric_huge())
        l_dest_code.setStyleSheet(f"color: {Theme.Colors.TEXT_PRIMARY}; border: none;")
        l_dest_city = QLabel(self.model.dest_city)
        l_dest_city.setFont(Theme.Fonts.caption())
        l_dest_city.setStyleSheet(f"color: {Theme.Colors.TEXT_MUTED}; border: none;")
        dest_box.addWidget(l_dest_code)
        dest_box.addWidget(l_dest_city)
        route_row.addLayout(dest_box)

        c3.main_layout.addLayout(route_row)

        # Barra de Progresso Real-time
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(self.model.progress_pct)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setStyleSheet(f"""
            QProgressBar {{
                background-color: {Theme.Colors.BORDER};
                border: none;
                height: 3px;
                border-radius: 1px;
            }}
            QProgressBar::chunk {{
                background-color: {Theme.Colors.PRIMARY};
                border-radius: 1px;
            }}
        """)
        c3.main_layout.addWidget(self.progress_bar)

        # Telemetry metrics row
        metrics_row = QHBoxLayout()

        m1 = QVBoxLayout()
        m1.setSpacing(2)
        l_m1_tag = QLabel("AIRCRAFT")
        l_m1_tag.setFont(Theme.Fonts.caption())
        l_m1_tag.setStyleSheet(f"color: {Theme.Colors.TEXT_MUTED}; border: none; font-size: 8px; letter-spacing: 1px;")
        l_m1_val = QLabel(self.model.aircraft_type)
        l_m1_val.setFont(Theme.Fonts.body_bold())
        l_m1_val.setStyleSheet(f"color: {Theme.Colors.TEXT_PRIMARY}; border: none;")
        m1.addWidget(l_m1_tag)
        m1.addWidget(l_m1_val)
        metrics_row.addLayout(m1)

        metrics_row.addStretch()

        m2 = QVBoxLayout()
        m2.setSpacing(2)
        l_m2_tag = QLabel("DURATION")
        l_m2_tag.setFont(Theme.Fonts.caption())
        l_m2_tag.setStyleSheet(f"color: {Theme.Colors.TEXT_MUTED}; border: none; font-size: 8px; letter-spacing: 1px;")
        l_m2_val = QLabel(self.model.duration)
        l_m2_val.setFont(Theme.Fonts.body_bold())
        l_m2_val.setStyleSheet(f"color: {Theme.Colors.TEXT_PRIMARY}; border: none;")
        m2.addWidget(l_m2_tag)
        m2.addWidget(l_m2_val)
        metrics_row.addLayout(m2)

        metrics_row.addStretch()

        m3 = QVBoxLayout()
        m3.setSpacing(2)
        l_m3_tag = QLabel("DISTANCE")
        l_m3_tag.setFont(Theme.Fonts.caption())
        l_m3_tag.setStyleSheet(f"color: {Theme.Colors.TEXT_MUTED}; border: none; font-size: 8px; letter-spacing: 1px;")
        self.l_m3_val = QLabel(f"{self.model.dist_from_str} / {self.model.distance}")
        self.l_m3_val.setFont(Theme.Fonts.body_bold())
        self.l_m3_val.setStyleSheet(f"color: {Theme.Colors.TEXT_PRIMARY}; border: none;")
        m3.addWidget(l_m3_tag)
        m3.addWidget(self.l_m3_val)
        metrics_row.addLayout(m3)

        c3.main_layout.addLayout(metrics_row)

        self.l_c3_sub = QLabel(f"{self.model.status_str} · ETA {self.model.eta} · Live Radar Active")
        self.l_c3_sub.setFont(Theme.Fonts.caption())
        self.l_c3_sub.setStyleSheet(f"color: {Theme.Colors.TEXT_MUTED}; border: none; font-size: 9px;")
        c3.main_layout.addWidget(self.l_c3_sub)

        layout.addWidget(c3)
        layout.addStretch()

        self.model.data_changed.connect(self.update_from_model)

    def _on_add_clicked(self) -> None:
        flight = self.input_flight.text()
        date = self.input_date.text()
        self.model.set_active_flight(flight, date)

    def update_from_model(self) -> None:
        flight = self.model.active_flight
        self.l_fn.setText(f"{flight}  ACTIVE")
        self.l_center_plane.setText(f"✈  {flight}")
        self.l_info1.setText(f"{self.model.status_str} · ETA {self.model.eta}")
        self.l_c3_sub.setText(f"{self.model.status_str} · ETA {self.model.eta} · Live Radar Active")
        self.progress_bar.setValue(self.model.progress_pct)
        self.l_m3_val.setText(f"{self.model.dist_from_str} / {self.model.distance}")
