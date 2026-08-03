"""
Testes — Event Bus
====================
Testa todas as funcionalidades do EventBus:
    - subscribe / unsubscribe
    - publish (síncrono e assíncrono)
    - handlers síncronos e assíncronos
    - histórico de eventos
    - estatísticas
    - constantes Events
"""

import asyncio
from collections import defaultdict

import pytest

from core.event_bus import Event, EventBus, Events


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def bus() -> EventBus:
    """Retorna um EventBus limpo para cada teste."""
    return EventBus()


# ---------------------------------------------------------------------------
# Testes: Subscribe
# ---------------------------------------------------------------------------


class TestEventBusSubscribe:
    def test_subscribe_as_decorator(self, bus: EventBus) -> None:
        @bus.subscribe("test.event")
        def handler(event: Event) -> None:
            pass

        assert "handler" in bus.get_subscribers("test.event")

    def test_subscribe_direct(self, bus: EventBus) -> None:
        def my_handler(event: Event) -> None:
            pass

        bus.subscribe("test.event", handler=my_handler)
        assert "my_handler" in bus.get_subscribers("test.event")

    def test_subscribe_many_handlers_to_same_event(self, bus: EventBus) -> None:
        def h1(e: Event) -> None: pass
        def h2(e: Event) -> None: pass
        def h3(e: Event) -> None: pass

        bus.subscribe("multi.event", handler=h1)
        bus.subscribe("multi.event", handler=h2)
        bus.subscribe("multi.event", handler=h3)

        subs = bus.get_subscribers("multi.event")
        assert len(subs) == 3

    def test_subscribe_many_events(self, bus: EventBus) -> None:
        def handler(e: Event) -> None: pass

        bus.subscribe_many(["event.a", "event.b", "event.c"], handler=handler)

        assert "handler" in bus.get_subscribers("event.a")
        assert "handler" in bus.get_subscribers("event.b")
        assert "handler" in bus.get_subscribers("event.c")

    def test_unsubscribe_existing_handler(self, bus: EventBus) -> None:
        def handler(e: Event) -> None: pass

        bus.subscribe("test.event", handler=handler)
        removed = bus.unsubscribe("test.event", handler)
        assert removed is True
        assert "handler" not in bus.get_subscribers("test.event")

    def test_unsubscribe_nonexistent_returns_false(self, bus: EventBus) -> None:
        def handler(e: Event) -> None: pass
        assert bus.unsubscribe("nao.existe", handler) is False


# ---------------------------------------------------------------------------
# Testes: Publish (síncrono)
# ---------------------------------------------------------------------------


class TestEventBusPublish:
    def test_publish_calls_handler(self, bus: EventBus) -> None:
        received: list[Event] = []

        @bus.subscribe("aircraft.updated")
        def handler(event: Event) -> None:
            received.append(event)

        bus.publish("aircraft.updated", data={"count": 5})
        assert len(received) == 1
        assert received[0].data == {"count": 5}

    def test_publish_passes_event_name(self, bus: EventBus) -> None:
        received: list[Event] = []

        bus.subscribe("iss.position_updated", handler=lambda e: received.append(e))
        bus.publish("iss.position_updated", data={"lat": 10.0})

        assert received[0].name == "iss.position_updated"

    def test_publish_passes_source(self, bus: EventBus) -> None:
        received: list[Event] = []
        bus.subscribe("weather.updated", handler=lambda e: received.append(e))
        bus.publish("weather.updated", source="weather_service")

        assert received[0].source == "weather_service"

    def test_publish_to_multiple_handlers(self, bus: EventBus) -> None:
        counts: dict[str, int] = defaultdict(int)

        def h1(e: Event) -> None: counts["h1"] += 1
        def h2(e: Event) -> None: counts["h2"] += 1
        def h3(e: Event) -> None: counts["h3"] += 1

        bus.subscribe("multi.event", handler=h1)
        bus.subscribe("multi.event", handler=h2)
        bus.subscribe("multi.event", handler=h3)

        notified = bus.publish("multi.event")
        assert notified == 3
        assert counts == {"h1": 1, "h2": 1, "h3": 1}

    def test_publish_returns_zero_for_no_subscribers(self, bus: EventBus) -> None:
        result = bus.publish("event.sem.subscribers")
        assert result == 0

    def test_publish_event_with_no_data(self, bus: EventBus) -> None:
        received: list[Event] = []
        bus.subscribe("app.started", handler=lambda e: received.append(e))
        bus.publish("app.started")

        assert received[0].data is None

    def test_publish_handler_exception_does_not_stop_others(
        self, bus: EventBus
    ) -> None:
        results: list[str] = []

        def bad_handler(e: Event) -> None:
            raise ValueError("Handler com erro")

        def good_handler(e: Event) -> None:
            results.append("ok")

        bus.subscribe("test.error", handler=bad_handler)
        bus.subscribe("test.error", handler=good_handler)
        bus.publish("test.error")

        # O bom handler ainda deve ser chamado
        assert "ok" in results

    def test_different_events_dont_cross(self, bus: EventBus) -> None:
        aircraft_events: list[Event] = []
        iss_events: list[Event] = []

        bus.subscribe("aircraft.updated", handler=lambda e: aircraft_events.append(e))
        bus.subscribe("iss.position_updated", handler=lambda e: iss_events.append(e))

        bus.publish("aircraft.updated", data="aircraft_data")
        bus.publish("iss.position_updated", data="iss_data")

        assert len(aircraft_events) == 1
        assert len(iss_events) == 1
        assert aircraft_events[0].data == "aircraft_data"
        assert iss_events[0].data == "iss_data"


# ---------------------------------------------------------------------------
# Testes: Publish Assíncrono
# ---------------------------------------------------------------------------


class TestEventBusAsync:
    @pytest.mark.asyncio
    async def test_publish_async_calls_async_handler(self, bus: EventBus) -> None:
        received: list[Event] = []

        @bus.subscribe("iss.position_updated")
        async def async_handler(event: Event) -> None:
            received.append(event)

        await bus.publish_async("iss.position_updated", data={"lat": 51.5})
        assert len(received) == 1
        assert received[0].data == {"lat": 51.5}

    @pytest.mark.asyncio
    async def test_publish_async_mixed_handlers(self, bus: EventBus) -> None:
        results: list[str] = []

        @bus.subscribe("mixed.event")
        def sync_handler(e: Event) -> None:
            results.append("sync")

        @bus.subscribe("mixed.event")
        async def async_handler(e: Event) -> None:
            results.append("async")

        await bus.publish_async("mixed.event")
        assert "sync" in results
        assert "async" in results


# ---------------------------------------------------------------------------
# Testes: Histórico
# ---------------------------------------------------------------------------


class TestEventBusHistory:
    def test_history_records_published_events(self, bus: EventBus) -> None:
        bus.publish("aircraft.updated", data={"n": 1})
        bus.publish("aircraft.updated", data={"n": 2})

        history = bus.get_history("aircraft.updated")
        assert len(history) == 2

    def test_history_filter_by_event_name(self, bus: EventBus) -> None:
        bus.publish("aircraft.updated", data={"n": 1})
        bus.publish("iss.position_updated", data={"lat": 0})
        bus.publish("aircraft.updated", data={"n": 2})

        aircraft_history = bus.get_history("aircraft.updated")
        assert len(aircraft_history) == 2

    def test_history_limit(self, bus: EventBus) -> None:
        for i in range(10):
            bus.publish("test.event", data=i)

        history = bus.get_history(limit=3)
        assert len(history) == 3


# ---------------------------------------------------------------------------
# Testes: Estatísticas e Utilitários
# ---------------------------------------------------------------------------


class TestEventBusStats:
    def test_stats_empty_bus(self, bus: EventBus) -> None:
        stats = bus.stats()
        assert stats["total_events_registered"] == 0
        assert stats["total_handlers"] == 0

    def test_stats_with_subscribers(self, bus: EventBus) -> None:
        def h1(e: Event) -> None: pass
        def h2(e: Event) -> None: pass

        bus.subscribe("event.a", handler=h1)
        bus.subscribe("event.a", handler=h2)
        bus.subscribe("event.b", handler=h1)

        stats = bus.stats()
        assert stats["total_handlers"] == 3

    def test_get_all_events(self, bus: EventBus) -> None:
        def h(e: Event) -> None: pass
        bus.subscribe("event.x", handler=h)
        bus.subscribe("event.y", handler=h)

        events = bus.get_all_events()
        assert "event.x" in events
        assert "event.y" in events

    def test_clear_all_subscribers(self, bus: EventBus) -> None:
        def h(e: Event) -> None: pass
        bus.subscribe("event.a", handler=h)
        bus.subscribe("event.b", handler=h)
        bus.clear_all_subscribers()

        assert bus.get_all_events() == []


# ---------------------------------------------------------------------------
# Testes: Constantes Events
# ---------------------------------------------------------------------------


class TestEvents:
    def test_events_constants_are_strings(self) -> None:
        assert isinstance(Events.AIRCRAFT_UPDATED, str)
        assert isinstance(Events.ISS_POSITION_UPDATED, str)
        assert isinstance(Events.WEATHER_UPDATED, str)
        assert isinstance(Events.APP_STARTED, str)

    def test_events_format_is_correct(self) -> None:
        """Todos os eventos devem seguir o padrão 'namespace.acao'."""
        event_values = [
            v for k, v in Events.__dict__.items()
            if not k.startswith("_")
        ]
        for event_name in event_values:
            assert "." in event_name, f"Evento sem namespace: {event_name}"


# ---------------------------------------------------------------------------
# Testes: Event Model
# ---------------------------------------------------------------------------


class TestEventModel:
    def test_event_has_timestamp(self) -> None:
        event = Event(name="test.event", data={"x": 1}, source="test")
        assert event.timestamp is not None

    def test_event_repr(self) -> None:
        event = Event(name="test.event", source="module_x")
        repr_str = repr(event)
        assert "test.event" in repr_str
        assert "module_x" in repr_str
