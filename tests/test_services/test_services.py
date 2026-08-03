"""
Testes — Service Layer
=======================
Testa a lógica de negócio dos serviços:
    - BaseService: ciclo de update com sucesso, salvamento em LocalStorage, publicação no EventBus e registro no ModuleManager
    - BaseService: fallback para LocalStorage em caso de erro na API e sinalização de erro no ModuleManager
    - Integração de AircraftService, WeatherService, ISSService, LaunchService e NASAService
"""

import pytest
import respx
import httpx

from core.event_bus import EventBus, Events
from core.module_manager import ModuleManager, ModuleState
from storage.local_storage import LocalStorage
from services.base_service import BaseService
from services.aircraft_service import AircraftService
from services.weather_service import WeatherService
from services.iss_service import ISSService
from services.launch_service import LaunchService
from services.nasa_service import NASAService
from models.common import Coordinate, DataSource
from models.space import ISSPosition


# ---------------------------------------------------------------------------
# Dummy Service para teste unitário puro do BaseService
# ---------------------------------------------------------------------------


class DummyService(BaseService[dict]):
    def __init__(self, should_fail: bool = False) -> None:
        super().__init__(module_name="aircraft", event_name="dummy.updated")
        self.should_fail = should_fail

    async def _fetch_from_api(self) -> dict:
        if self.should_fail:
            raise RuntimeError("API timeout simulation")
        return {"data": "ok"}


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def service_env(tmp_path, monkeypatch: pytest.MonkeyPatch):
    """
    Configura ambiente isolado para o EventBus, ModuleManager e LocalStorage.
    """
    import core.event_bus as eb_mod
    import core.module_manager as mm_mod
    import storage.local_storage as ls_mod
    import services.base_service as bs_mod

    bus = EventBus()
    mgr = ModuleManager()
    storage = LocalStorage(base_dir=tmp_path)

    mgr.register("aircraft", "Radar", "Desc", enabled_by_config=True)
    mgr.register("weather", "Clima", "Desc", enabled_by_config=True)
    mgr.register("iss", "ISS", "Desc", enabled_by_config=True)
    mgr.register("launch", "Launch", "Desc", enabled_by_config=True)
    mgr.register("nasa", "NASA", "Desc", enabled_by_config=True)

    mgr.enable("aircraft")
    mgr.enable("weather")
    mgr.enable("iss")
    mgr.enable("launch")
    mgr.enable("nasa")

    import sys
    monkeypatch.setattr(sys.modules["core.event_bus"], "event_bus", bus)
    monkeypatch.setattr(sys.modules["core.module_manager"], "module_manager", mgr)
    monkeypatch.setattr(sys.modules["storage.local_storage"], "local_storage", storage)
    monkeypatch.setattr(sys.modules["services.base_service"], "event_bus", bus)
    monkeypatch.setattr(sys.modules["services.base_service"], "module_manager", mgr)
    monkeypatch.setattr(sys.modules["services.base_service"], "local_storage", storage)

    return {"bus": bus, "mgr": mgr, "storage": storage}


# ---------------------------------------------------------------------------
# Testes do BaseService
# ---------------------------------------------------------------------------


class TestBaseService:
    @pytest.mark.asyncio
    async def test_update_success_flow(self, service_env: dict) -> None:
        events_received = []
        service_env["bus"].subscribe("dummy.updated", handler=lambda e: events_received.append(e))

        srv = DummyService(should_fail=False)
        result = await srv.update()

        assert result == {"data": "ok"}
        assert len(events_received) == 1
        assert events_received[0].data == {"data": "ok"}
        assert service_env["mgr"].get("aircraft").update_count == 1
        assert service_env["storage"].load_latest("aircraft")["data"] == "ok"

    @pytest.mark.asyncio
    async def test_update_failure_with_fallback(self, service_env: dict) -> None:
        # Primeiro salva um dado no LocalStorage
        service_env["storage"].save("aircraft", {"data": "old_saved"})

        srv = DummyService(should_fail=True)
        result = await srv.update()

        # Deve retornar o dado fallback do LocalStorage
        assert result["data"] == "old_saved"
        assert service_env["mgr"].get("aircraft").state == ModuleState.ERROR

    @pytest.mark.asyncio
    async def test_update_ignored_when_module_inactive(self, service_env: dict) -> None:
        service_env["mgr"].disable("aircraft")

        srv = DummyService(should_fail=False)
        result = await srv.update()

        assert result is None
        assert service_env["mgr"].get("aircraft").update_count == 0


# ---------------------------------------------------------------------------
# Testes dos Serviços Concretos
# ---------------------------------------------------------------------------


class TestConcreteServices:
    @pytest.mark.asyncio
    @respx.mock
    async def test_iss_service_update(self, service_env: dict) -> None:
        mock_data = {
            "name": "iss",
            "id": 25544,
            "latitude": -10.0,
            "longitude": -50.0,
            "altitude": 415.0,
            "velocity": 27600.0,
            "visibility": "daylight",
            "timestamp": 1722689000,
        }
        respx.get("https://api.wheretheiss.at/v1/satellites/25544").mock(
            return_value=httpx.Response(200, json=mock_data)
        )

        srv = ISSService()
        result = await srv.update()

        assert isinstance(result, ISSPosition)
        assert result.position.latitude == -10.0
        assert service_env["mgr"].get("iss").update_count == 1
