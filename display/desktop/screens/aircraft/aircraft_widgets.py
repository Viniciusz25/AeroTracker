"""
AeroTracker Core — Aircraft Widgets
====================================
Widgets reutilizáveis específicos da tela de aeronaves.
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QHBoxLayout, QLabel, QVBoxLayout, QWidget
from display.components.animated_card import AnimatedCard
from display.components.status_badge import StatusBadge
from display.theme import Theme
from models.aircraft import AircraftState


class AircraftCardWidget(AnimatedCard):
    """
    Card estilizado para representar o estado de uma aeronave individual.
    """

    def __init__(self, aircraft: AircraftState, parent=None) -> None:
        super().__init__(parent)
        self.aircraft = aircraft

        # Layout Superior: Callsign e Badge de Status
        top_layout = QHBoxLayout()
        top_layout.setContentsMargins(0, 0, 0, 0)

        callsign = f"✈  {aircraft.display_id}"
        self.lbl_callsign = QLabel(callsign)
        self.lbl_callsign.setFont(Theme.Fonts.card_title())
        self.lbl_callsign.setStyleSheet(f"color: {Theme.Colors.TEXT_PRIMARY}; border: none;")
        top_layout.addWidget(self.lbl_callsign)
        top_layout.addStretch()

        badge_type = "warning" if aircraft.on_ground else "success"
        status_text = "EM SOLO" if aircraft.on_ground else "EM VOO"
        self.badge = StatusBadge(status_text, badge_type=badge_type)
        top_layout.addWidget(self.badge)

        self.main_layout.addLayout(top_layout)

        # Informações Técnicas
        country = aircraft.origin_country or "Desconhecido"
        alt_str = f"{aircraft.altitude_m:,.0f} m" if aircraft.altitude_m is not None else "N/A"
        speed_str = f"{aircraft.speed_kmh:,.0f} km/h" if aircraft.speed_kmh is not None else "N/A"
        heading_str = f"{aircraft.heading:.0f}°" if aircraft.heading is not None else "N/A"
        pos_str = str(aircraft.position) if aircraft.position else "Sem GPS"

        info1 = f"🏳 {country}   |   📐 Altitude: {alt_str}   |   ⚡ Velocidade: {speed_str}"
        info2 = f"🧭 Proa: {heading_str}   |   📍 GPS: {pos_str}   |   ICAO24: {aircraft.icao24.upper()}"

        self.lbl_info1 = QLabel(info1)
        self.lbl_info1.setFont(Theme.Fonts.body())
        self.lbl_info1.setStyleSheet(f"color: {Theme.Colors.TEXT_PRIMARY}; border: none;")
        self.main_layout.addWidget(self.lbl_info1)

        self.lbl_info2 = QLabel(info2)
        self.lbl_info2.setFont(Theme.Fonts.caption())
        self.lbl_info2.setStyleSheet(f"color: {Theme.Colors.TEXT_SECONDARY}; border: none;")
        self.main_layout.addWidget(self.lbl_info2)
