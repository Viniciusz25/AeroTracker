"""
AeroTracker Core — Aircraft View (MVC)
======================================
View pura do Radar de Aeronaves com layout responsivo e mapa vetorial.
"""

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QHBoxLayout, QLabel, QScrollArea, QVBoxLayout, QWidget

from display.components.primary_button import AnimatedButton
from display.components.vector_map_widget import VectorMapWidget
from display.desktop.screens.aircraft.aircraft_model import AircraftModel
from display.desktop.screens.aircraft.aircraft_widgets import AircraftCardWidget
from display.theme import Theme


class AircraftView(QWidget):
    """
    View do Radar de Aeronaves integrando mapa vetorial e lista de cards.
    """

    refresh_requested = Signal()

    def __init__(self, model: AircraftModel, parent=None) -> None:
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
        self.lbl_title.setFont(Theme.Fonts.title_section())
        self.lbl_title.setStyleSheet(f"color: {Theme.Colors.TEXT_PRIMARY};")
        header_layout.addWidget(self.lbl_title)
        header_layout.addStretch()

        self.btn_refresh = AnimatedButton("🔄 Atualizar Agora", is_primary=True)
        self.btn_refresh.clicked.connect(self.refresh_requested.emit)
        header_layout.addWidget(self.btn_refresh)
        self.main_layout.addLayout(header_layout)

        # Status Summary Label
        self.lbl_status = QLabel(self.model.status_text)
        self.lbl_status.setFont(Theme.Fonts.body())
        self.lbl_status.setStyleSheet(f"color: {Theme.Colors.PRIMARY};")
        self.main_layout.addWidget(self.lbl_status)

        # Split Content (Mapa Vetorial à esquerda, Lista à direita)
        content_layout = QHBoxLayout()
        content_layout.setSpacing(Theme.Dimensions.PAD_M)

        # Mapa Vetorial de Radar
        self.vector_map = VectorMapWidget(radius_km=250.0)
        self.vector_map.setMinimumSize(360, 360)
        content_layout.addWidget(self.vector_map, stretch=1)

        # Área rolável de cards
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_layout.setContentsMargins(0, 0, 0, 0)
        self.scroll_layout.setSpacing(Theme.Dimensions.PAD_S)
        self.scroll_layout.addStretch()
        self.scroll_area.setWidget(self.scroll_content)

        content_layout.addWidget(self.scroll_area, stretch=2)
        self.main_layout.addLayout(content_layout)

        # Conecta sinal do Model para atualização
        self.model.data_changed.connect(self.update_from_model)
        self.model.status_changed.connect(self._on_status_changed)

    def update_from_model(self) -> None:
        """Atualiza os componentes da View quando o Model muda."""
        self.lbl_status.setText(self.model.status_text)

        # Limpa cards anteriores
        for i in reversed(range(self.scroll_layout.count() - 1)):
            item = self.scroll_layout.itemAt(i)
            if item and item.widget():
                item.widget().deleteLater()

        # Renderiza novos cards
        aircraft_list = self.model.aircraft_list
        for ac in aircraft_list:
            card = AircraftCardWidget(ac)
            self.scroll_layout.insertWidget(self.scroll_layout.count() - 1, card)

        # Atualiza marcadores vetoriais no mapa de radar
        self.vector_map.update_aircraft_markers(aircraft_list)

    def _on_status_changed(self, msg: str) -> None:
        self.lbl_status.setText(msg)
