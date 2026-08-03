"""
AeroTracker Core — SolarSystem Model (MVC)
===========================================
Modelo de dados do Sistema Solar.
"""

from PySide6.QtCore import QObject, Signal


class SolarSystemModel(QObject):
    """
    Model do Sistema Solar.
    """

    data_changed = Signal()

    def __init__(self) -> None:
        super().__init__()
        self._title_text = "🪐 SOLAR SYSTEM OBSERVATORY — EFEMÉRIDES PLANETÁRIAS"
        self._bodies = [
            ("Mercury", "0.387 AU", "Orbital Period: 88 days"),
            ("Venus", "0.723 AU", "Orbital Period: 225 days"),
            ("Mars", "1.524 AU", "Orbital Period: 687 days"),
            ("Jupiter", "5.203 AU", "Orbital Period: 11.8 years"),
            ("Saturn", "9.537 AU", "Orbital Period: 29.4 years"),
        ]

    @property
    def title_text(self) -> str:
        return self._title_text

    @property
    def bodies(self) -> list[tuple[str, str, str]]:
        return self._bodies
