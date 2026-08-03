"""
AeroTracker Core — Componente FlightTrackerGauge (Mostrador Circular de Voo)
==========================================================================
Gauge circular de acompanhamento de voo em tempo real inspirado em hardware 
de aviação tática / cockpits modernos.
"""

import math
from PySide6.QtCore import Property, QEasingCurve, QPropertyAnimation, QPointF, QRectF, Qt
from PySide6.QtGui import QBrush, QColor, QFont, QPainter, QPainterPath, QPen
from PySide6.QtWidgets import QWidget
from display.theme import Theme


class FlightTrackerGauge(QWidget):
    """
    Mostrador circular de acompanhamento de voo (Flight Tracker Display).
    """

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setMinimumSize(380, 380)

        # Dados do Voo
        self.aircraft_type = "Airbus A319 114"
        self.callsign = "DL3073"
        self.origin_code = "LAX"
        self.origin_city = "Los Angeles"
        self.dest_code = "SJC"
        self.dest_city = "San Jose"
        self.altitude_str = "15 m"
        self.speed_str = "217 km/h"
        self.heading_str = "NNW"
        self.source_str = "OPENSKY DAL3073"

        # Progresso da Rota (0.0 a 1.0)
        self._progress = 0.75

        # Animação do Indicador de Progresso
        self._anim = QPropertyAnimation(self, b"progress", self)
        self._anim.setDuration(1200)
        self._anim.setEasingCurve(QEasingCurve.Type.OutQuad)

    def get_progress(self) -> float:
        return self._progress

    def set_progress(self, val: float) -> None:
        self._progress = max(0.0, min(1.0, val))
        self.update()

    progress = Property(float, get_progress, set_progress)

    def animate_to_progress(self, target: float) -> None:
        self._anim.stop()
        self._anim.setStartValue(self._progress)
        self._anim.setEndValue(target)
        self._anim.start()

    def update_flight_data(
        self,
        callsign: str,
        aircraft_type: str,
        origin_code: str,
        origin_city: str,
        dest_code: str,
        dest_city: str,
        altitude_str: str,
        speed_str: str,
        heading_str: str,
        progress: float = 0.75,
    ) -> None:
        self.callsign = callsign
        self.aircraft_type = aircraft_type
        self.origin_code = origin_code
        self.origin_city = origin_city
        self.dest_code = dest_code
        self.dest_city = dest_city
        self.altitude_str = altitude_str
        self.speed_str = speed_str
        self.heading_str = heading_str
        self.animate_to_progress(progress)

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        size = min(self.width(), self.height())
        center_x = self.width() / 2.0
        center_y = self.height() / 2.0
        radius = (size / 2.0) - 15

        # 1. Moldura Circular Metálica (Bezel)
        painter.setPen(QPen(QColor("#2C3440"), 8))
        painter.setBrush(QBrush(QColor("#000000")))
        painter.drawEllipse(QPointF(center_x, center_y), radius, radius)

        # Anel Interno sutil
        painter.setPen(QPen(QColor("#151D28"), 2))
        painter.drawEllipse(QPointF(center_x, center_y), radius - 6, radius - 6)

        # 2. Ícone de Cia Aérea (Triângulo Delta Vermelho no Topo)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(QColor("#FF3355")))
        top_y = center_y - radius + 35
        p1 = QPointF(center_x, top_y - 12)
        p2 = QPointF(center_x - 10, top_y + 6)
        p3 = QPointF(center_x + 10, top_y + 6)
        path_delta = QPainterPath()
        path_delta.moveTo(p1)
        path_delta.lineTo(p2)
        path_delta.lineTo(p3)
        path_delta.closeSubpath()
        painter.drawPath(path_delta)

        # 3. Silhueta da Aeronave Verde Neon
        plane_y = center_y - radius + 75
        self._draw_plane_silhouette(painter, center_x, plane_y)

        # Modelo da Aeronave
        painter.setPen(QPen(QColor(Theme.Colors.TEXT_PRIMARY)))
        painter.setFont(QFont("Segoe UI", 9, QFont.Weight.Medium))
        painter.drawText(
            QRectF(center_x - 100, plane_y + 22, 200, 20),
            Qt.AlignmentFlag.AlignCenter,
            self.aircraft_type,
        )

        # 4. Arco Parabólico da Rota
        arc_y_start = center_y - 15
        arc_x_left = center_x - radius + 45
        arc_x_right = center_x + radius - 45
        arc_height = 55

        arc_path = QPainterPath()
        arc_path.moveTo(arc_x_left, arc_y_start)
        arc_path.quadTo(center_x, arc_y_start - arc_height, arc_x_right, arc_y_start)

        painter.setPen(QPen(QColor("#FFB300"), 3, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawPath(arc_path)

        # Ponto de Posição da Aeronave no Arco
        t = self._progress
        # Curva de Bézier quadrática P(t) = (1-t)^2 * P0 + 2(1-t)t * P1 + t^2 * P2
        dot_x = ((1 - t) ** 2) * arc_x_left + 2 * (1 - t) * t * center_x + (t**2) * arc_x_right
        dot_y = ((1 - t) ** 2) * arc_y_start + 2 * (1 - t) * t * (arc_y_start - arc_height) + (t**2) * arc_y_start

        # Brilho do ponto branco
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(QColor(255, 255, 255, 100)))
        painter.drawEllipse(QPointF(dot_x, dot_y), 7, 7)
        painter.setBrush(QBrush(QColor("#FFFFFF")))
        painter.drawEllipse(QPointF(dot_x, dot_y), 4, 4)

        # Rótulos Origem (Esquerda) e Destino (Direita)
        painter.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        painter.setPen(QPen(QColor(Theme.Colors.TEXT_PRIMARY)))
        painter.drawText(QRectF(arc_x_left - 45, arc_y_start - 12, 60, 24), Qt.AlignmentFlag.AlignCenter, self.origin_code)
        painter.drawText(QRectF(arc_x_right - 15, arc_y_start - 12, 60, 24), Qt.AlignmentFlag.AlignCenter, self.dest_code)

        painter.setFont(QFont("Segoe UI", 8))
        painter.setPen(QPen(QColor(Theme.Colors.TEXT_SECONDARY)))
        painter.drawText(QRectF(arc_x_left - 55, arc_y_start + 12, 80, 16), Qt.AlignmentFlag.AlignCenter, self.origin_city)
        painter.drawText(QRectF(arc_x_right - 25, arc_y_start + 12, 80, 16), Qt.AlignmentFlag.AlignCenter, self.dest_city)

        # 5. Callsign Principal Central
        painter.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        painter.setPen(QPen(QColor(Theme.Colors.TEXT_PRIMARY)))
        painter.drawText(QRectF(center_x - 100, center_y + 25, 200, 32), Qt.AlignmentFlag.AlignCenter, self.callsign)

        # 6. Três Emblemas Circulares de Telemetria (Rodapé Interno)
        badge_y = center_y + 75
        self._draw_telemetry_badge(painter, center_x - 70, badge_y, "alt", self.altitude_str)
        self._draw_telemetry_badge(painter, center_x, badge_y, "speed", self.speed_str)
        self._draw_telemetry_badge(painter, center_x + 70, badge_y, "heading", self.heading_str)

        # 7. Fonte de Dados (OPENSKY)
        painter.setFont(QFont("Consolas", 8))
        painter.setPen(QPen(QColor("#475569")))
        painter.drawText(QRectF(center_x - 120, center_y + radius - 30, 240, 18), Qt.AlignmentFlag.AlignCenter, self.source_str)

    def _draw_plane_silhouette(self, painter: QPainter, cx: float, cy: float) -> None:
        """Desenha silhueta vetorial da aeronave em verde neon."""
        painter.setPen(QPen(QColor("#00FF66"), 2, Qt.PenStyle.SolidLine))
        painter.setBrush(Qt.BrushStyle.NoBrush)

        path = QPainterPath()
        # Bico da aeronave virado para a direita
        path.moveTo(cx + 25, cy)
        path.quadTo(cx + 10, cy - 6, cx - 15, cy - 6)
        path.lineTo(cx - 15, cy - 18)  # Asa da cauda top
        path.lineTo(cx - 22, cy - 18)
        path.lineTo(cx - 20, cy - 6)
        path.lineTo(cx - 30, cy - 6)
        path.lineTo(cx - 35, cy)
        path.lineTo(cx - 30, cy + 6)
        path.lineTo(cx - 20, cy + 6)
        path.lineTo(cx - 22, cy + 18)  # Asa da cauda bot
        path.lineTo(cx - 15, cy + 18)
        path.lineTo(cx - 15, cy + 6)
        path.quadTo(cx + 10, cy + 6, cx + 25, cy)
        path.closeSubpath()

        # Asa principal
        path.moveTo(cx + 5, cy - 6)
        path.lineTo(cx - 5, cy - 25)
        path.lineTo(cx - 12, cy - 25)
        path.lineTo(cx - 3, cy - 6)

        path.moveTo(cx + 5, cy + 6)
        path.lineTo(cx - 5, cy + 25)
        path.lineTo(cx - 12, cy + 25)
        path.lineTo(cx - 3, cy + 6)

        painter.drawPath(path)

    def _draw_telemetry_badge(self, painter: QPainter, bx: float, by: float, badge_type: str, val_str: str) -> None:
        """Desenha emblema circular com ícone verde e valor."""
        # Círculo do Emblema
        painter.setPen(QPen(QColor("#00FF66"), 1.5))
        painter.setBrush(QBrush(QColor("#051B10")))
        painter.drawEllipse(QPointF(bx, by), 15, 15)

        # Ícone no interior do círculo
        painter.setPen(QPen(QColor("#00FF66"), 1.5))
        if badge_type == "alt":
            # Seta vertical / Régua
            painter.drawLine(QPointF(bx, by + 6), QPointF(bx, by - 6))
            painter.drawLine(QPointF(bx - 3, by - 3), QPointF(bx, by - 6))
            painter.drawLine(QPointF(bx + 3, by - 3), QPointF(bx, by - 6))
        elif badge_type == "speed":
            # Arcodômetro
            arc = QRectF(bx - 7, by - 7, 14, 14)
            painter.drawArc(arc, 0 * 16, 180 * 16)
            painter.drawLine(QPointF(bx, by + 2), QPointF(bx + 4, by - 3))
        elif badge_type == "heading":
            # Bússola / Seta Direcional
            painter.drawLine(QPointF(bx - 4, by + 4), QPointF(bx + 4, by - 4))
            painter.drawLine(QPointF(bx + 4, by - 4), QPointF(bx + 1, by - 4))
            painter.drawLine(QPointF(bx + 4, by - 4), QPointF(bx + 4, by - 1))

        # Texto do Valor
        painter.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        painter.setPen(QPen(QColor(Theme.Colors.TEXT_PRIMARY)))
        painter.drawText(QRectF(bx - 40, by + 18, 80, 18), Qt.AlignmentFlag.AlignCenter, val_str)
