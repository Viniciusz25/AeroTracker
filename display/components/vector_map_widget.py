"""
AeroTracker Core — Componente VectorMapWidget (Mapa Vetorial)
=============================================================
Renderização vetorial de radar aéreo com QGraphicsView e QGraphicsScene.
Exibe anéis de alcance, eixos cardeais e marcadores vetoriais das aeronaves.
"""

import math
from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QBrush, QColor, QFont, QPainter, QPen
from PySide6.QtWidgets import QGraphicsEllipseItem, QGraphicsLineItem, QGraphicsScene, QGraphicsTextItem, QGraphicsView

from display.theme import Theme


class VectorMapWidget(QGraphicsView):
    """
    Mapa e radar vetorial renderizado com QGraphicsScene (desenho vetorial puro).
    """

    def __init__(self, radius_km: float = 250.0, parent=None) -> None:
        super().__init__(parent)
        self.radius_km = radius_km

        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)

        # Configurações de anti-aliasing e renderização vetorial
        self.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        self.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True)
        self.setStyleSheet(f"""
            QGraphicsView {{
                background-color: {Theme.Colors.BG_DARK};
                border: 1px solid {Theme.Colors.BORDER};
                border-radius: {Theme.Dimensions.RADIUS_CARD}px;
            }}
        """)

        self.center_lat = -23.5505
        self.center_lon = -46.6333
        self.view_size = 400.0

        self.scene.setSceneRect(
            -self.view_size / 2,
            -self.view_size / 2,
            self.view_size,
            self.view_size,
        )

        self._draw_vector_grid()

    def _draw_vector_grid(self) -> None:
        """Desenha a grade e anéis concêntricos vetoriais do radar."""
        self.scene.clear()

        pen_ring = QPen(QColor(Theme.Colors.BORDER_LIGHT))
        pen_ring.setStyle(Qt.PenStyle.DashLine)
        pen_ring.setWidth(1)

        pen_axis = QPen(QColor(Theme.Colors.BORDER))
        pen_axis.setWidth(1)

        # Eixos vetoriais X/Y
        r = self.view_size / 2 - 20
        self.scene.addLine(-r, 0, r, 0, pen_axis)
        self.scene.addLine(0, -r, 0, r, pen_axis)

        # Anéis de alcance concêntricos vetoriais (50km, 100km, 150km, 200km, 250km)
        num_rings = 4
        for i in range(1, num_rings + 1):
            ring_r = (r / num_rings) * i
            self.scene.addEllipse(
                -ring_r, -ring_r, ring_r * 2, ring_r * 2, pen_ring
            )

        # Textos cardeais vetoriais
        font = QFont(Theme.Fonts.FONT_FAMILY, 9, QFont.Weight.Bold)
        for label_text, x, y in [("N", 0, -r + 5), ("S", 0, r - 20), ("E", r - 15, -10), ("W", -r + 5, -10)]:
            t_item = QGraphicsTextItem(label_text)
            t_item.setFont(font)
            t_item.setDefaultTextColor(QColor(Theme.Colors.PRIMARY))
            t_item.setPos(x, y)
            self.scene.addItem(t_item)

    def set_center(self, lat: float, lon: float) -> None:
        self.center_lat = lat
        self.center_lon = lon
        self._draw_vector_grid()

    def update_aircraft_markers(self, aircraft_list: list) -> None:
        """Plota marcadores vetoriais das aeronaves em coordenadas polares transformadas."""
        self._draw_vector_grid()

        r_max = self.view_size / 2 - 20
        pen_plane = QPen(QColor(Theme.Colors.AIRBORNE))
        pen_plane.setWidth(2)
        brush_plane = QBrush(QColor(Theme.Colors.AIRBORNE))

        pen_ground = QPen(QColor(Theme.Colors.ON_GROUND))
        brush_ground = QBrush(QColor(Theme.Colors.ON_GROUND))

        for ac in aircraft_list:
            lat = getattr(ac, "latitude", None) or (ac.position.latitude if getattr(ac, "position", None) else None)
            lon = getattr(ac, "longitude", None) or (ac.position.longitude if getattr(ac, "position", None) else None)
            if lat is None or lon is None:
                continue

            # Conversão vetorial aproximada de lat/lon para coordenadas de tela
            d_lat = lat - self.center_lat
            d_lon = lon - self.center_lon
            # 1 grau lat ≈ 111km
            y_km = d_lat * 111.32
            x_km = d_lon * 111.32 * math.cos(math.radians(self.center_lat))

            dist_km = math.sqrt(x_km**2 + y_km**2)
            if dist_km > self.radius_km:
                continue

            screen_x = (x_km / self.radius_km) * r_max
            screen_y = -(y_km / self.radius_km) * r_max  # Y invertido na tela

            on_ground = getattr(ac, "on_ground", False)
            pen = pen_ground if on_ground else pen_plane
            brush = brush_ground if on_ground else brush_plane

            # Desenho vetorial do ponto da aeronave
            size = 6
            self.scene.addEllipse(screen_x - size / 2, screen_y - size / 2, size, size, pen, brush)

            # Rótulo vetorial com o callsign
            callsign = getattr(ac, "display_id", "") or getattr(ac, "callsign", "") or "AC"
            ac_label = QGraphicsTextItem(callsign)
            ac_label.setFont(QFont(Theme.Fonts.FONT_FAMILY, 8))
            ac_label.setDefaultTextColor(QColor(Theme.Colors.TEXT_PRIMARY))
            ac_label.setPos(screen_x + 5, screen_y - 10)
            self.scene.addItem(ac_label)
