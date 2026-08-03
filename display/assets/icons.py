"""
AeroTracker Core — Provedor de Ícones SVG (Assets)
=================================================
Centraliza a geração e renderização vetorial de todos os ícones da aplicação em formato SVG.
"""

from PySide6.QtCore import QByteArray, Qt
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtSvg import QSvgRenderer


class SVGIcons:
    """Provedor central de ícones vetoriais SVG."""

    PLANE = """<svg viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <path d="M17.8 19.2 16 11l3.5-3.5C21 6 21.5 4 21 3.5c-.5-.5-2.5 0-4 1.5L13.5 8.5 5.3 6.7c-.5-.1-1 .1-1.3.5l-.5.7c-.3.4-.2 1 .2 1.3L8.5 12 5 15.5H2.5L1 17l3.5 1 1 3.5 1.5-1.5v-2.5L10.5 14l2.8 4.8c.3.4.9.5 1.3.2l.7-.5c.4-.3.6-.8.5-1.3z"/>
    </svg>"""

    RADAR = """<svg viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <path d="M12 12m-9 0a9 9 0 1 0 18 0a9 9 0 1 0 -18 0"/>
        <path d="M12 12m-6 0a6 6 0 1 0 12 0a6 6 0 1 0 -12 0"/>
        <path d="M12 12m-3 0a3 3 0 1 0 6 0a3 3 0 1 0 -6 0"/>
        <path d="M12 12l6-6"/>
    </svg>"""

    WEATHER = """<svg viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <path d="M12 2v2m0 16v2M4.93 4.93l1.41 1.41m11.32 11.32l1.41 1.41M2 12h2m16 0h2M6.34 17.66l-1.41 1.41M19.07 4.93l-1.41 1.41"/>
        <circle cx="12" cy="12" r="5"/>
    </svg>"""

    DASHBOARD = """<svg viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <rect x="3" y="3" width="7" height="9" rx="1"/>
        <rect x="14" y="3" width="7" height="5" rx="1"/>
        <rect x="14" y="12" width="7" height="9" rx="1"/>
        <rect x="3" y="16" width="7" height="5" rx="1"/>
    </svg>"""

    REFRESH = """<svg viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <path d="M21.5 2v6h-6M21.34 15.57a10 10 0 1 1-.57-8.38l5.67-5.67"/>
    </svg>"""

    @classmethod
    def get_icon(cls, svg_template: str, color: str = "#00D2FF", size: int = 24) -> QIcon:
        """Converte o template SVG em um objeto QIcon com cor e tamanho especificados."""
        svg_bytes = svg_template.format(color=color).encode("utf-8")
        renderer = QSvgRenderer(QByteArray(svg_bytes))
        pixmap = QPixmap(size, size)
        pixmap.fill(Qt.GlobalColor.transparent)
        from PySide6.QtGui import QPainter
        painter = QPainter(pixmap)
        renderer.render(painter)
        painter.end()
        return QIcon(pixmap)
