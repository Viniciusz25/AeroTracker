"""
Testes — Module Manager
========================
Testa o ciclo de vida dos módulos:
    - registro
    - ativação / desativação
    - estados (ACTIVE, INACTIVE, ERROR)
    - record_update
    - status e consultas
    - integração com EventBus
"""

import pytest

from core.event_bus import EventBus, Events
from core.module_manager import ModuleInfo, ModuleManager, ModuleState


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def bus() -> EventBus:
    """EventBus isolado para cada teste."""
    return EventBus()


@pytest.fixture
def manager(bus: EventBus, monkeypatch: pytest.MonkeyPatch) -> ModuleManager:
    """
    ModuleManager isolado usando EventBus local.

    Usa sys.modules para obter o módulo Python e monkeypatch
    para substituir a referência local ao event_bus.
    """
    import sys
    mm_module = sys.modules["core.module_manager"]
    monkeypatch.setattr(mm_module, "event_bus", bus)
    return ModuleManager()




# ---------------------------------------------------------------------------
# Testes: Registro
# ---------------------------------------------------------------------------


class TestModuleManagerRegister:
    def test_register_basic_module(self, manager: ModuleManager) -> None:
        info = manager.register(
            name="aircraft",
            display_name="Radar de Aeronaves",
            description="Teste",
            interval_seconds=3,
            enabled_by_config=True,
        )
        assert info.name == "aircraft"
        assert info.display_name == "Radar de Aeronaves"
        assert info.interval_seconds == 3

    def test_register_enabled_module_starts_as_registered(
        self, manager: ModuleManager
    ) -> None:
        info = manager.register("iss", "ISS", "Teste", enabled_by_config=True)
        assert info.state == ModuleState.REGISTERED

    def test_register_disabled_module_starts_as_inactive(
        self, manager: ModuleManager
    ) -> None:
        info = manager.register("satellites", "Satélites", "Teste", enabled_by_config=False)
        assert info.state == ModuleState.INACTIVE

    def test_register_duplicate_returns_existing(self, manager: ModuleManager) -> None:
        manager.register("weather", "Clima", "Desc1")
        info2 = manager.register("weather", "Clima Novo", "Desc2")
        # Deve retornar o já existente sem sobrescrever
        assert info2.description == "Desc1"

    def test_get_all_modules_after_register(self, manager: ModuleManager) -> None:
        manager.register("aircraft", "A", "D1")
        manager.register("iss", "I", "D2")
        manager.register("weather", "W", "D3")

        all_mods = manager.get_all_modules()
        names = [m.name for m in all_mods]
        assert "aircraft" in names
        assert "iss" in names
        assert "weather" in names


# ---------------------------------------------------------------------------
# Testes: Ativação / Desativação
# ---------------------------------------------------------------------------


class TestModuleManagerEnableDisable:
    def test_enable_registered_module(self, manager: ModuleManager) -> None:
        manager.register("aircraft", "A", "D")
        result = manager.enable("aircraft")
        assert result is True
        assert manager.is_active("aircraft")

    def test_enable_already_active_returns_true(self, manager: ModuleManager) -> None:
        manager.register("aircraft", "A", "D")
        manager.enable("aircraft")
        result = manager.enable("aircraft")  # segunda chamada
        assert result is True

    def test_enable_nonexistent_returns_false(self, manager: ModuleManager) -> None:
        result = manager.enable("nao_existe")
        assert result is False

    def test_disable_active_module(self, manager: ModuleManager) -> None:
        manager.register("weather", "W", "D")
        manager.enable("weather")
        result = manager.disable("weather")
        assert result is True
        assert not manager.is_active("weather")

    def test_disable_already_inactive_returns_true(self, manager: ModuleManager) -> None:
        manager.register("moon", "M", "D", enabled_by_config=False)
        result = manager.disable("moon")
        assert result is True

    def test_disable_nonexistent_returns_false(self, manager: ModuleManager) -> None:
        result = manager.disable("nao_existe")
        assert result is False

    def test_is_active_returns_false_for_unregistered(
        self, manager: ModuleManager
    ) -> None:
        assert manager.is_active("modulo_fantasma") is False


# ---------------------------------------------------------------------------
# Testes: Estados
# ---------------------------------------------------------------------------


class TestModuleManagerStates:
    def test_set_error_changes_state(self, manager: ModuleManager) -> None:
        manager.register("aircraft", "A", "D")
        manager.enable("aircraft")
        manager.set_error("aircraft", "Timeout na API")

        info = manager.get("aircraft")
        assert info.state == ModuleState.ERROR
        assert info.error_message == "Timeout na API"

    def test_record_update_increments_count(self, manager: ModuleManager) -> None:
        manager.register("iss", "I", "D")
        manager.enable("iss")
        manager.record_update("iss")
        manager.record_update("iss")
        manager.record_update("iss")

        info = manager.get("iss")
        assert info.update_count == 3

    def test_record_update_sets_last_updated_at(self, manager: ModuleManager) -> None:
        manager.register("weather", "W", "D")
        manager.enable("weather")
        manager.record_update("weather")

        info = manager.get("weather")
        assert info.last_updated_at is not None

    def test_record_update_recovers_from_error(self, manager: ModuleManager) -> None:
        manager.register("aircraft", "A", "D")
        manager.enable("aircraft")
        manager.set_error("aircraft", "Erro temporário")

        assert manager.get("aircraft").state == ModuleState.ERROR

        manager.record_update("aircraft")

        info = manager.get("aircraft")
        assert info.state == ModuleState.ACTIVE
        assert info.error_message is None


# ---------------------------------------------------------------------------
# Testes: Consultas
# ---------------------------------------------------------------------------


class TestModuleManagerQueries:
    def test_get_active_modules(self, manager: ModuleManager) -> None:
        manager.register("aircraft", "A", "D")
        manager.register("iss", "I", "D")
        manager.register("moon", "M", "D", enabled_by_config=False)

        manager.enable("aircraft")
        manager.enable("iss")

        active = manager.get_active_modules()
        active_names = [m.name for m in active]
        assert "aircraft" in active_names
        assert "iss" in active_names
        assert "moon" not in active_names

    def test_status_returns_counts(self, manager: ModuleManager) -> None:
        manager.register("aircraft", "A", "D")
        manager.register("iss", "I", "D")
        manager.register("moon", "M", "D", enabled_by_config=False)

        manager.enable("aircraft")
        manager.enable("iss")

        status = manager.status()
        assert status["total"] == 3
        assert status["active"] == 2
        assert status["inactive"] == 1

    def test_get_nonexistent_returns_none(self, manager: ModuleManager) -> None:
        assert manager.get("fantasma") is None

    def test_module_info_to_dict(self, manager: ModuleManager) -> None:
        manager.register("launch", "Lançamentos", "Desc", interval_seconds=600)
        manager.enable("launch")
        manager.record_update("launch")

        info = manager.get("launch")
        d = info.to_dict()

        assert d["name"] == "launch"
        assert d["state"] == "active"
        assert d["interval_seconds"] == 600
        assert d["update_count"] == 1
        assert d["last_updated_at"] is not None


# ---------------------------------------------------------------------------
# Testes: Integração com EventBus
# ---------------------------------------------------------------------------


class TestModuleManagerEvents:
    def test_enable_publishes_module_enabled_event(
        self, manager: ModuleManager, bus: EventBus
    ) -> None:
        received: list = []
        bus.subscribe(Events.MODULE_ENABLED, handler=lambda e: received.append(e))

        manager.register("aircraft", "A", "D")
        manager.enable("aircraft")

        assert len(received) == 1
        assert received[0].data["name"] == "aircraft"

    def test_disable_publishes_module_disabled_event(
        self, manager: ModuleManager, bus: EventBus
    ) -> None:
        received: list = []
        bus.subscribe(Events.MODULE_DISABLED, handler=lambda e: received.append(e))

        manager.register("iss", "I", "D")
        manager.enable("iss")
        manager.disable("iss")

        assert len(received) == 1
        assert received[0].data["name"] == "iss"

    def test_set_error_publishes_error_api_event(
        self, manager: ModuleManager, bus: EventBus
    ) -> None:
        errors: list = []
        bus.subscribe(Events.ERROR_API, handler=lambda e: errors.append(e))

        manager.register("weather", "W", "D")
        manager.enable("weather")
        manager.set_error("weather", "Timeout")

        assert len(errors) == 1
        assert errors[0].data["module"] == "weather"
