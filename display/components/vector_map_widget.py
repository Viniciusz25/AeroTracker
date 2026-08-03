"""
AeroTracker Core — Componente VectorRadarWidget (Radar ATC Vetorial)
====================================================================
Radar vetorial de alta precisão inspirado em displays ATC (Air Traffic Control)
e Garmin G1000 Navigation Display.
"""

import math
from PySide6.QtCore import QEasingCurve, QPropertyAnimation, QRectF, Qt, Property
from PySide6.QtGui import QBrush, QColor, QFont, QPainter, QPen, QPolygonF
from PySide6.QtWidgets import QGraphicsEllipseItem, QGraphicsLineItem, QGraphicsPolygonItem, QGraphicsScene, QGraphicsTextItem, QGraphicsView

from display.theme import Theme


class VectorRadarWidget(QGraphicsView):
    """
    Radar ATC vetorial com varredura contínua, anéis de alcance e vetores de rumo.
    """

    def __init__(self, radius_km: float = 250.0, parent=None) -> None:
        super().__init__(parent)
        self.radius_km = radius_km

        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)

        self.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        self.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True)

        self.setStyleSheet(f"""
            QGraphicsView {{
                background-color: {Theme.Colors.BG_DARK};
                border: 1px solid {Theme.Colors.BORDER};
                border-radius: {Theme.Dimensions.RADIUS_PANEL}px;
            }}
        """)

        self.center_lat = -23.5505
        self.center_lon = -46.6333
        self.view_size = 420.0

        self.scene.setSceneRect(
            -self.view_size / 2,
            -self.view_size / 2,
            self.view_size,
            self.view_size,
        )

        self._sweep_angle = 0.0
        self._sweep_line = None
        self._draw_vector_grid()

    def _draw_vector_grid(self) -> None:
        """Desenha a grade geográfica vetorial e os anéis concêntricos de alcance."""
        self.scene.clear()

        pen_ring = QPen(QColor(Theme.Colors.BORDER))
        pen_ring.setStyle(Qt.PenStyle.DashLine)
        pen_ring.setWidth(1)

        pen_axis = QPen(QColor(Theme.Colors.BG_CARD))
        pen_axis.setWidth(1)

        r = self.view_size / 2 - 25

        # Grade geográfica e eixos ortogonais
        self.scene.addLine(-r, 0, r, 0, pen_axis)
        self.scene.addLine(0, -r, 0, r, pen_axis)

        # Anéis de alcance vetoriais (50km, 100km, 150km, 200km, 250km)
        num_rings = 4
        for i in range(1, num_rings + 1):
            ring_r = (r / num_rings) * i
            self.scene.addEllipse(-ring_r, -ring_r, ring_r * 2, ring_r * 2, pen_ring)

        # Linha de varredura do radar
        pen_sweep = QPen(QColor(Theme.Colors.CYAN_NEON))
        pen_sweep.setWidth(1)
        rad = math.radians(self._sweep_angle)
        self._sweep_line = self.scene.addLine(
            0, 0, r * math.cos(rad), r * math.sin(rad), pen_sweep
        )

        # Bússola e coordenadas cardeais (N, S, E, W)
        font = QFont(Theme.Fonts.FONT_MONO, 9, QFont.Weight.Bold)
        for label_text, x, y in [("N", -4, -r + 5), ("S", -4, r - 18), ("E", r - 15, -8), ("W", -r + 5, -8)]:
            t_item = QGraphicsTextItem(label_text)
            t_item.setFont(font)
            t_item.setDefaultTextColor(QColor(Theme.Colors.CYAN_NEON))
            t_item.setPos(x, y)
            self.scene.addItem(t_item)

    def update_aircraft_markers(self, aircraft_list: list) -> None:
        """Plota marcadores e vetores de rumo das aeronaves."""
        self._draw_vector_grid()

        r_max = self.view_size / 2 - 25
        pen_plane = QPen(QColor(Theme.Colors.POSITIVE))
        pen_plane.setWidth(2)
        brush_plane = QBrush(QColor(Theme.Colors.POSITIVE))

        pen_ground = QPen(QColor(Theme.Colors.ATTENTION))
        brush_ground = QBrush(QColor(Theme.Colors.ATTENTION))

        for ac in aircraft_list:
            lat = getattr(ac, "latitude", None) or (ac.position.latitude if getattr(ac, "position", None) else None)
            lon = getattr(ac, "longitude", None) or (ac.position.longitude if getattr(ac, "position", None) else None)
            if lat is None or lon is None:
                continue

            d_lat = lat - self.center_lat
            d_lon = lon - self.center_lon
            y_km = d_lat * 111.32
            x_km = d_lon * 111.32 * math.cos(math.radians(self.center_lat))

            dist_km = math.sqrt(x_km**2 + y_km**2)
            if dist_km > self.radius_km:
                continue

            screen_x = (x_km / self.radius_km) * r_max
            screen_y = -(y_km / self.radius_km) * r_max

            on_ground = getattr(ac, "on_ground", False)
            pen = pen_ground if on_ground else pen_plane
            brush = brush_ground if on_ground else brush_plane

            # Marcador em formato vetorial de triângulo para direção do voo
            heading = getattr(ac, "heading", 0.0) or 0.0
            heading_rad = math.radians(heading - 90)

            # Triângulo vetorial representando a aeronave em movimento
            size = 8
            p1 = QPointF(screen_x + size * math.cos(heading_rad), screen_y + size * math.sin(heading_rad))
            p2 = QPointF(screen_x + (size / 2) * math.cos(heading_rad + 2.4), screen_y + (size / 2) * math.sin(heading_rad + 2.4))
            p3 = QPointF(screen_x + (size / 2) * math.cos(heading_rad - 2.4), screen_y + (size / 2) * math.sin(heading_rad - 2.4))

            polygon = QPolygonF([p1, p2, p3])
            self.scene.addPolygon(polygon, pen, brush)

            # Linha de vetor de rumo (Heading Vector)
            vec_len = 15
            self.scene.addLine(
                screen_x,
                screen_y,
                screen_x + vec_len * math.cos(heading_rad),
                screen_y + vec_len * math.sin(heading_rad),
                pen,
            )

            # Rótulo de chamada (Callsign)
            callsign = getattr(ac, "display_id", "") or getattr(ac, "callsign", "") or "AC"
            ac_label = QGraphicsTextItem(callsign)
            ac_label.setFont(QFont(Theme.Fonts.FONT_MONO, 8))
            ac_label.setDefaultTextColor(QColor(Theme.Colors.TEXT_PRIMARY))
            ac_label.setPos(screen_x + 8, screen_y - 8)
            self.scene.addItem(ac_label)


# Alias de compatibilidade
VectorMapWidget = VectorRadarWidget
