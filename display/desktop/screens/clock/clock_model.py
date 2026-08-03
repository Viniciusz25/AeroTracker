"""
AeroTracker Core — Clock Model (MVC)
====================================
Modelo de dados do cronômetro aeroespacial UTC/MET.
"""

from datetime import datetime, timezone
from PySide6.QtCore import QObject, QTimer, Signal


class ClockModel(QObject):
    """
    Model da tela Clock.
    """

    time_updated = Signal()

    def __init__(self) -> None:
        super().__init__()
        self._title_text = "⏱ AEROSPACE CHRONOMETER — TEMPO UTC & MET"
        self._timer = QTimer(self)
        self._timer.setInterval(1000)
        self._timer.timeout.connect(self._tick)
        self._timer.start()

    @property
    def title_text(self) -> str:
        return self._title_text

    @property
    def utc_time_str(self) -> str:
        return datetime.now(timezone.utc).strftime("%H:%M:%S UTC")

    @property
    def local_time_str(self) -> str:
        return datetime.now().strftime("%H:%M:%S LOCAL")

    @property
    def utc_date_str(self) -> str:
        return datetime.now(timezone.utc).strftime("%Y-%m-%d")

    def _tick(self) -> None:
        self.time_updated.emit()
