"""
AeroTracker Core — Componente DevicePreviewWidget (Device Digital Twin)
========================================================================
Painel de simulação em tempo real para exibições de hardware embarcado
(Display Circular ESP32-S3 466x466 AMOLED / LCD) correspondente ao Airspace Companion.
"""

import math
from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QBrush, QColor, QFont, QPainter, QPainterPath, QPen
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QVBoxLayout, QWidget
from display.theme import Theme


class DeviceCircleDisplay(QWidget):
    """
    Mostrador gráfico circular de 466x466 AMOLED simulando o visor do ESP32-S3.
    """

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setMinimumSize(290, 290)
        self.setMaximumSize(320, 320)

        # Dados Padrão de Voo no Visor ESP32
        self.flight_number = "YP113"
        self.origin_code = "ICN"
        self.origin_city = "Seoul"
        self.dest_code = "SFO"
        self.dest_city = "San Francisco"
        self.dist_from = "0 km"
        self.dist_to = "9107 km"
        self.duration_str = "11h 00m"
        self.eta_str = "13:00"

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w = self.width()
        h = self.height()
        center_x = w / 2.0
        center_y = h / 2.0
        radius = (min(w, h) / 2.0) - 15

        # 1. Anel de Brilho Ambiente Esmeralda (Aura Ring)
        glow_pen = QPen(QColor(71, 243, 160, 40), 12)
        painter.setPen(glow_pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawEllipse(QPointF(center_x, center_y), radius + 4, radius + 4)

        # 2. Tela Circular Preto Absoluto (AMOLED)
        painter.setPen(QPen(QColor(Theme.Colors.BORDER), 2))
        painter.setBrush(QBrush(QColor("#000000")))
        painter.drawEllipse(QPointF(center_x, center_y), radius, radius)

        # 3. Ícone Delta Superior e Número do Voo
        top_y = center_y - radius + 25
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(QColor(Theme.Colors.ALERT)))
        p1 = QPointF(center_x, top_y - 8)
        p2 = QPointF(center_x - 6, top_y + 4)
        p3 = QPointF(center_x + 6, top_y + 4)
        delta_path = QPainterPath()
        delta_path.moveTo(p1)
        delta_path.lineTo(p2)
        delta_path.lineTo(p3)
        delta_path.closeSubpath()
        painter.drawPath(delta_path)

        painter.setFont(QFont("Consolas", 10, QFont.Weight.Bold))
        painter.setPen(QPen(QColor(Theme.Colors.TEXT_PRIMARY)))
        painter.drawText(QRectF(center_x - 60, top_y + 10, 120, 18), Qt.AlignmentFlag.AlignCenter, self.flight_number)

        # 4. Projeção Cartográfica Global (Continente em linhas escuras)
        painter.setPen(QPen(QColor("#1A2421"), 1))
        # Linha do Equador e Meridianos
        painter.drawEllipse(QPointF(center_x, center_y - 10), radius - 30, (radius - 30) * 0.6)
        painter.drawLine(QPointF(center_x - radius + 25, center_y - 10), QPointF(center_x + radius - 25, center_y - 10))

        # 5. Arco de Voo Tracejado em Verde Neon (ICN -> SFO)
        arc_path = QPainterPath()
        arc_x1 = center_x - radius + 35
        arc_y1 = center_y + 10
        arc_x2 = center_x + radius - 35
        arc_y2 = center_y - 5
        arc_path.moveTo(arc_x1, arc_y1)
        arc_path.quadTo(center_x, center_y - radius + 55, arc_x2, arc_y2)

        dashed_pen = QPen(QColor(Theme.Colors.PRIMARY), 1.8, Qt.PenStyle.DashLine)
        painter.setPen(dashed_pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawPath(arc_path)

        # Ícone de Aeronave em ICN
        painter.setPen(QPen(QColor(Theme.Colors.PRIMARY), 1.5))
        painter.drawEllipse(QPointF(arc_x1, arc_y1), 5, 5)

        # Rótulos ICN e SFO
        painter.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        painter.setPen(QPen(QColor(Theme.Colors.TEXT_PRIMARY)))
        painter.drawText(QRectF(arc_x1 - 35, arc_y1 - 10, 30, 16), Qt.AlignmentFlag.AlignCenter, self.origin_code)
        painter.drawText(QRectF(arc_x2 + 5, arc_y2 - 10, 30, 16), Qt.AlignmentFlag.AlignCenter, self.dest_code)

        painter.setFont(QFont("Segoe UI", 7))
        painter.setPen(QPen(QColor(Theme.Colors.TEXT_SECONDARY)))
        painter.drawText(QRectF(arc_x1 - 40, arc_y1 + 5, 40, 14), Qt.AlignmentFlag.AlignCenter, self.origin_city)
        painter.drawText(QRectF(arc_x2 + 2, arc_y2 + 5, 50, 14), Qt.AlignmentFlag.AlignCenter, self.dest_city)

        # 6. Painel de Métricas Inferiores no Visor
        bot_y = center_y + 40
        painter.setFont(QFont("Segoe UI", 7))
        painter.setPen(QPen(QColor(Theme.Colors.TEXT_MUTED)))
        painter.drawText(QRectF(center_x - 110, bot_y, 100, 12), Qt.AlignmentFlag.AlignCenter, f"FROM {self.origin_code}")
        painter.drawText(QRectF(center_x + 10, bot_y, 100, 12), Qt.AlignmentFlag.AlignCenter, f"TO {self.dest_code}")

        painter.setFont(QFont("Consolas", 8, QFont.Weight.Bold))
        painter.setPen(QPen(QColor(Theme.Colors.TEXT_PRIMARY)))
        painter.drawText(QRectF(center_x - 110, bot_y + 12, 100, 14), Qt.AlignmentFlag.AlignCenter, self.dist_from)
        painter.drawText(QRectF(center_x + 10, bot_y + 12, 100, 14), Qt.AlignmentFlag.AlignCenter, self.dist_to)

        bot_y2 = bot_y + 30
        painter.setFont(QFont("Segoe UI", 7))
        painter.setPen(QPen(QColor(Theme.Colors.TEXT_MUTED)))
        painter.drawText(QRectF(center_x - 110, bot_y2, 100, 12), Qt.AlignmentFlag.AlignCenter, "DURATION")
        painter.drawText(QRectF(center_x + 10, bot_y2, 100, 12), Qt.AlignmentFlag.AlignCenter, "ETA")

        painter.setFont(QFont("Consolas", 8, QFont.Weight.Bold))
        painter.setPen(QPen(QColor(Theme.Colors.TEXT_PRIMARY)))
        painter.drawText(QRectF(center_x - 110, bot_y2 + 12, 100, 14), Qt.AlignmentFlag.AlignCenter, self.duration_str)
        painter.drawText(QRectF(center_x + 10, bot_y2 + 12, 100, 14), Qt.AlignmentFlag.AlignCenter, self.eta_str)

        # Indicador de Carrossel de Páginas (Pontos)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(QColor(Theme.Colors.PRIMARY)))
        painter.drawEllipse(QPointF(center_x - 8, center_y + radius - 20), 3, 3)
        painter.setBrush(QBrush(QColor(Theme.Colors.TEXT_MUTED)))
        painter.drawEllipse(QPointF(center_x, center_y + radius - 20), 2.5, 2.5)
        painter.drawEllipse(QPointF(center_x + 8, center_y + radius - 20), 2.5, 2.5)


class DevicePreviewPanel(QFrame):
    """
    Painel completo do Device Digital Twin (Área 3 à direita no layout).
    """

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setFixedWidth(310)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {Theme.Colors.BG_SIDEBAR};
                border-left: 1px solid {Theme.Colors.BORDER};
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(Theme.Dimensions.PAD_M, Theme.Dimensions.PAD_M, Theme.Dimensions.PAD_M, Theme.Dimensions.PAD_M)
        layout.setSpacing(Theme.Dimensions.PAD_S)

        # 1. Cabeçalho Digital Twin
        lbl_head = QLabel("DEVICE DIGITAL TWIN")
        lbl_head.setFont(Theme.Fonts.caption())
        lbl_head.setStyleSheet(f"color: {Theme.Colors.TEXT_MUTED}; border: none;")
        lbl_head.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(lbl_head)

        lbl_sub = QLabel("Flight • 9 ➔ 3")
        lbl_sub.setFont(Theme.Fonts.title_section())
        lbl_sub.setStyleSheet(f"color: {Theme.Colors.TEXT_PRIMARY}; border: none;")
        lbl_sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(lbl_sub)

        # 2. Mostrador Circular AMOLED 466x466
        self.circle_display = DeviceCircleDisplay(self)
        layout.addWidget(self.circle_display, alignment=Qt.AlignmentFlag.AlignCenter)

        lbl_swipe = QLabel("MAIN • SWIPE DOWN FOR 6 + 12")
        lbl_swipe.setFont(Theme.Fonts.caption())
        lbl_swipe.setStyleSheet(f"color: {Theme.Colors.TEXT_MUTED}; border: none;")
        lbl_swipe.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(lbl_swipe)

        layout.addStretch()

        # 3. Caixa de Status de Sincronização do Hardware ESP32 (Rodapé Direito)
        status_box = QFrame()
        status_box.setStyleSheet(f"""
            QFrame {{
                background-color: {Theme.Colors.BG_CARD};
                border: 1px solid {Theme.Colors.BORDER};
                border-radius: {Theme.Dimensions.RADIUS_M}px;
            }}
        """)
        s_layout = QVBoxLayout(status_box)
        s_layout.setContentsMargins(Theme.Dimensions.PAD_S, Theme.Dimensions.PAD_S, Theme.Dimensions.PAD_S, Theme.Dimensions.PAD_S)
        s_layout.setSpacing(Theme.Dimensions.PAD_XS)

        s_layout.addLayout(self._create_status_row("CONFIG", "Device and companion config synchronized"))
        s_layout.addLayout(self._create_status_row("DEVICE", "Pushed Cartographic Glass to ESP32"))
        s_layout.addLayout(self._create_status_row("RENDER", "Saved YP113_route_map_466.png"))

        layout.addWidget(status_box)

    def _create_status_row(self, tag: str, text: str) -> QHBoxLayout:
        row = QHBoxLayout()
        lbl_tag = QLabel(tag)
        lbl_tag.setFont(Theme.Fonts.caption())
        lbl_tag.setStyleSheet(f"color: {Theme.Colors.TEXT_MUTED}; border: none;")
        lbl_tag.setFixedWidth(50)

        lbl_val = QLabel(f"🟢 {text}")
        lbl_val.setFont(Theme.Fonts.caption())
        lbl_val.setStyleSheet(f"color: {Theme.Colors.PRIMARY}; border: none;")

        row.addWidget(lbl_tag)
        row.addWidget(lbl_val)
        return row
