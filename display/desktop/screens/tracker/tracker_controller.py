"""
AeroTracker Core — Tracker Controller (MVC)
===========================================
Controller intermediador para o módulo Tracker conectado com OpenSky Network em tempo real.
"""

from PySide6.QtCore import QObject, QTimer
from core.event_bus import Event, Events, event_bus
from display.desktop.screens.tracker.tracker_model import TrackerModel
from utils.logger import get_logger

logger = get_logger(__name__)


class TrackerController(QObject):
    """
    Controller do módulo Tracker conectado aos voos em tempo real da OpenSky.
    """

    def __init__(self, model: TrackerModel, service=None) -> None:
        super().__init__()
        self.model = model
        self.service = service

        # Inscreve no barramento de eventos para atualizações da OpenSky
        event_bus.subscribe(Events.AIRCRAFT_UPDATED, handler=self._on_aircraft_updated)

        # Temporizador de Telemetria de Fallback / Suavização
        self.timer = QTimer(self)
        self.timer.setInterval(2000)
        self.timer.timeout.connect(self._on_realtime_tick)
        self.timer.start()

        if self.service and self.service.last_data:
            self._process_realtime_aircraft(self.service.last_data)

    def add_flight(self, flight_number: str, departure_date: str = "") -> None:
        """Adiciona e ativa um novo voo no monitoramento em tempo real."""
        self.model.set_active_flight(flight_number, departure_date)
        if self.service and self.service.last_data:
            self._process_realtime_aircraft(self.service.last_data)

    def sync_flight(self) -> None:
        if self.service:
            self._process_realtime_aircraft(self.service.last_data)
        else:
            self.model.data_changed.emit()

    def _on_aircraft_updated(self, event: Event) -> None:
        """Recebe snapshot de voos reais da OpenSky via EventBus."""
        if event.data is not None:
            self._process_realtime_aircraft(event.data)

    def _process_realtime_aircraft(self, data) -> None:
        """Filtra e vincula os dados reais de radar da OpenSky ao modelo."""
        aircraft_list = []
        if hasattr(data, "aircraft") and data.aircraft:
            aircraft_list = data.aircraft
        elif hasattr(data, "states") and data.states:
            aircraft_list = data.states
        elif isinstance(data, list):
            aircraft_list = data

        if not aircraft_list:
            return

        target_callsign = self.model.active_flight.strip().upper()
        selected_ac = None

        # 1. Procura por correspondência exata ou parcial de callsign
        for ac in aircraft_list:
            cs = getattr(ac, "callsign", "") or ""
            if target_callsign in cs.strip().upper():
                selected_ac = ac
                break

        # 2. Se não encontrar o callsign exato, escolhe a aeronave em voo com maior velocidade
        if not selected_ac:
            airborne_ac = [ac for ac in aircraft_list if not getattr(ac, "on_ground", False)]
            if airborne_ac:
                selected_ac = airborne_ac[0]
            else:
                selected_ac = aircraft_list[0]

        # 3. Extrai a telemetria real da aeronave selecionada
        callsign = (getattr(selected_ac, "callsign", None) or target_callsign).strip()
        country = getattr(selected_ac, "origin_country", "International") or "Brazil"

        # Velocidade em km/h
        vel_obj = getattr(selected_ac, "velocity", None)
        if hasattr(vel_obj, "in_kmh"):
            speed_kmh = vel_obj.in_kmh
        elif isinstance(vel_obj, (int, float)):
            speed_kmh = vel_obj * 3.6
        else:
            speed_kmh = 850.0

        # Altitude em metros / pés
        alt_obj = getattr(selected_ac, "altitude", None)
        if hasattr(alt_obj, "meters"):
            alt_m = alt_obj.meters
        elif isinstance(alt_obj, (int, float)):
            alt_m = alt_obj
        else:
            alt_m = 10600.0

        alt_fl = int(alt_m * 3.28084 / 100)

        # Atualiza a telemetria dinâmica no modelo
        status_str = f"LIVE OPENSKY · {speed_kmh:.0f} km/h · FL{alt_fl}"
        aircraft_type_str = f"{callsign} ({country})"

        self.model._aircraft_type = aircraft_type_str
        self.model.update_telemetry(
            progress_pct=(self.model.progress_pct + 1) % 100,
            dist_from_km=int(9107 * (self.model.progress_pct / 100.0)),
            dist_to_km=9107 - int(9107 * (self.model.progress_pct / 100.0)),
            status_str=status_str,
        )

    def _on_realtime_tick(self) -> None:
        """Avança a telemetria de voo quando não há pacote direto de radar."""
        if self.service and self.service.last_data:
            self._process_realtime_aircraft(self.service.last_data)
        else:
            new_pct = (self.model.progress_pct + 1) % 100
            total_dist = 9107
            dist_from = int(total_dist * (new_pct / 100.0))
            dist_to = total_dist - dist_from
            status = f"EN ROUTE · {new_pct}%"
            self.model.update_telemetry(new_pct, dist_from, dist_to, status)
