"""
AeroTracker Core — Tracker Controller (MVC)
===========================================
Controller intermediador para o módulo Tracker com temporizador de telemetria em tempo real.
"""

from PySide6.QtCore import QObject, QTimer
from display.desktop.screens.tracker.tracker_model import TrackerModel


class TrackerController(QObject):
    """
    Controller do módulo Tracker com atualização em tempo real.
    """

    def __init__(self, model: TrackerModel) -> None:
        super().__init__()
        self.model = model

        # Temporizador de Telemetria de Voo em Tempo Real (a cada 2.5s)
        self.timer = QTimer(self)
        self.timer.setInterval(2500)
        self.timer.timeout.connect(self._on_realtime_tick)
        self.timer.start()

    def add_flight(self, flight_number: str, departure_date: str = "") -> None:
        """Adiciona e ativa um novo voo no monitoramento."""
        self.model.set_active_flight(flight_number, departure_date)

    def sync_flight(self) -> None:
        self.model.data_changed.emit()

    def _on_realtime_tick(self) -> None:
        """Incrementa a posição e distância do voo ativo em tempo real."""
        new_pct = self.model.progress_pct + 1
        if new_pct > 100:
            new_pct = 0

        total_dist = 9107
        dist_from = int(total_dist * (new_pct / 100.0))
        dist_to = total_dist - dist_from

        if new_pct == 0:
            status = "BOARDING / TAXI"
        elif new_pct < 10:
            status = "CLIMBING · FL340"
        elif new_pct > 90:
            status = "DESCENT · APPROACH"
        else:
            status = f"EN ROUTE · {new_pct}%"

        self.model.update_telemetry(new_pct, dist_from, dist_to, status)
