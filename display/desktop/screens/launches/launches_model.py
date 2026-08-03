"""
AeroTracker Core — Launches Model (MVC)
=======================================
Modelo de dados da agenda de lançamentos espaciais.
"""

from PySide6.QtCore import QObject, Signal
from models.space import Launch


class LaunchesModel(QObject):
    """
    Model da tela de Lançamentos.
    """

    data_changed = Signal()

    def __init__(self) -> None:
        super().__init__()
        self._title_text = "🚀 SPACE LAUNCHES — AGENDA DE LANÇAMENTOS ESPACIAIS"
        self._launches: list[Launch] = []

    @property
    def title_text(self) -> str:
        return self._title_text

    @property
    def launches(self) -> list[Launch]:
        return self._launches

    def update_launches(self, data: list[Launch] | list) -> None:
        if isinstance(data, list):
            self._launches = data
        elif hasattr(data, "launches"):
            self._launches = data.launches

        self.data_changed.emit()
