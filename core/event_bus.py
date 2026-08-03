"""
AeroTracker Core — Event Bus (Barramento de Eventos)
======================================================
Sistema de comunicação pub/sub desacoplado entre módulos.

Responsabilidades:
    - Permitir que módulos publiquem eventos sem conhecer os assinantes
    - Permitir que módulos se inscrevam em eventos de interesse
    - Suporte a handlers síncronos e assíncronos
    - Thread-safe e async-safe
    - Registro de eventos para debug e auditoria

Design (Padrão Observer / Event Bus):
    - Publishers: qualquer módulo pode publicar eventos
    - Subscribers: qualquer módulo pode assinar eventos
    - Eventos são identificados por strings (ex: "aircraft.updated")
    - Desacoplamento total: publisher não conhece subscribers

Convenção de nomes de eventos:
    "<módulo>.<ação>"
    Exemplos:
        "aircraft.updated"       → nova lista de aeronaves disponível
        "iss.position_updated"   → nova posição da ISS
        "weather.updated"        → dados de clima atualizados
        "launch.upcoming_loaded" → lançamentos carregados
        "module.enabled"         → módulo foi ativado
        "module.disabled"        → módulo foi desativado
        "scheduler.tick"         → ciclo do scheduler
        "error.api"              → erro em chamada de API

Uso:
    from core.event_bus import event_bus, Event

    # Assinar evento
    @event_bus.subscribe("aircraft.updated")
    def on_aircraft_update(event: Event) -> None:
        print(f"Recebido: {event.data}")

    # Publicar evento
    event_bus.publish("aircraft.updated", data={"count": 42})

    # Assinar com handler assíncrono
    @event_bus.subscribe("iss.position_updated")
    async def on_iss_update(event: Event) -> None:
        await display.update_iss(event.data)
"""

import asyncio
import inspect
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import UTC, datetime
from threading import Lock
from typing import Any, Callable, Coroutine

from utils.logger import get_logger

logger = get_logger(__name__)

# Tipo para handlers: síncrono ou assíncrono
HandlerType = Callable[["Event"], Any]
AsyncHandlerType = Callable[["Event"], Coroutine[Any, Any, None]]


# ---------------------------------------------------------------------------
# Modelo de Evento
# ---------------------------------------------------------------------------


@dataclass
class Event:
    """
    Representa um evento publicado no barramento.

    Attributes:
        name: Identificador do evento (ex: "aircraft.updated").
        data: Payload do evento (qualquer dado serializável).
        source: Módulo que publicou o evento.
        timestamp: Momento de criação do evento (UTC).
    """

    name: str
    data: Any = None
    source: str = "unknown"
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))

    def __repr__(self) -> str:
        return (
            f"Event(name={self.name!r}, source={self.source!r}, "
            f"timestamp={self.timestamp.isoformat()})"
        )


# ---------------------------------------------------------------------------
# Event Bus
# ---------------------------------------------------------------------------


class EventBus:
    """
    Barramento de eventos pub/sub thread-safe.

    Suporta handlers síncronos e assíncronos.
    Handlers assíncronos são executados no event loop ativo quando disponível.
    """

    def __init__(self) -> None:
        # Mapa: nome_evento → lista de handlers
        self._handlers: dict[str, list[HandlerType]] = defaultdict(list)
        self._lock = Lock()
        # Histórico dos últimos N eventos para debug
        self._history: list[Event] = []
        self._history_max = 100

        logger.info("EventBus inicializado")

    # -------------------------------------------------------------------------
    # Subscrição
    # -------------------------------------------------------------------------

    def subscribe(
        self,
        event_name: str,
        handler: HandlerType | None = None,
    ) -> Callable:
        """
        Inscreve um handler em um evento.

        Pode ser usado como decorator ou chamado diretamente.

        Args:
            event_name: Nome do evento a assinar (ex: "aircraft.updated").
            handler: Função a chamar quando o evento for publicado.
                     Se None, retorna um decorator.

        Returns:
            Decorator (se handler=None) ou o próprio handler registrado.

        Exemplos:
            # Como decorator
            @event_bus.subscribe("aircraft.updated")
            def handle(event): ...

            # Direto
            event_bus.subscribe("aircraft.updated", handler=my_handler)
        """
        def decorator(fn: HandlerType) -> HandlerType:
            with self._lock:
                self._handlers[event_name].append(fn)
            logger.debug(
                "EventBus: '{fn}' inscrito em '{event}'",
                fn=fn.__name__, event=event_name
            )
            return fn

        if handler is not None:
            return decorator(handler)
        return decorator

    def unsubscribe(self, event_name: str, handler: HandlerType) -> bool:
        """
        Remove um handler de um evento.

        Args:
            event_name: Nome do evento.
            handler: Handler a remover.

        Returns:
            True se o handler existia e foi removido.
        """
        with self._lock:
            handlers = self._handlers.get(event_name, [])
            if handler in handlers:
                handlers.remove(handler)
                logger.debug(
                    "EventBus: '{fn}' removido de '{event}'",
                    fn=handler.__name__, event=event_name
                )
                return True
        return False

    def subscribe_many(
        self,
        events: list[str],
        handler: HandlerType,
    ) -> None:
        """
        Inscreve um handler em múltiplos eventos de uma vez.

        Args:
            events: Lista de nomes de eventos.
            handler: Handler a registrar em todos os eventos.
        """
        for event_name in events:
            self.subscribe(event_name, handler=handler)

    # -------------------------------------------------------------------------
    # Publicação
    # -------------------------------------------------------------------------

    def publish(
        self,
        event_name: str,
        data: Any = None,
        source: str = "unknown",
    ) -> int:
        """
        Publica um evento no barramento.

        Chama todos os handlers inscritos no evento.
        Handlers assíncronos são agendados no event loop ativo.

        Args:
            event_name: Nome do evento (ex: "aircraft.updated").
            data: Payload do evento.
            source: Identificador do módulo publicador.

        Returns:
            Número de handlers notificados.
        """
        event = Event(name=event_name, data=data, source=source)

        with self._lock:
            handlers = list(self._handlers.get(event_name, []))
            # Salvar no histórico
            self._history.append(event)
            if len(self._history) > self._history_max:
                self._history.pop(0)

        if not handlers:
            logger.debug(
                "EventBus PUBLISH: '{event}' — sem subscribers",
                event=event_name
            )
            return 0

        logger.debug(
            "EventBus PUBLISH: '{event}' → {n} handler(s) | source='{src}'",
            event=event_name, n=len(handlers), src=source
        )

        notified = 0
        for handler in handlers:
            try:
                if inspect.iscoroutinefunction(handler):
                    # Handler assíncrono: tentar usar event loop ativo
                    try:
                        loop = asyncio.get_running_loop()
                        loop.create_task(handler(event))
                    except RuntimeError:
                        # Sem event loop ativo: executar de forma síncrona
                        asyncio.run(handler(event))
                else:
                    handler(event)
                notified += 1
            except Exception as e:
                logger.error(
                    "EventBus: erro no handler '{fn}' para '{event}': {err}",
                    fn=handler.__name__, event=event_name, err=str(e)
                )

        return notified

    async def publish_async(
        self,
        event_name: str,
        data: Any = None,
        source: str = "unknown",
    ) -> int:
        """
        Publica um evento aguardando handlers assíncronos completarem.

        Use quando precisar garantir que todos os handlers async
        terminaram antes de continuar.

        Args:
            event_name: Nome do evento.
            data: Payload do evento.
            source: Identificador do módulo publicador.

        Returns:
            Número de handlers notificados.
        """
        event = Event(name=event_name, data=data, source=source)

        with self._lock:
            handlers = list(self._handlers.get(event_name, []))
            self._history.append(event)
            if len(self._history) > self._history_max:
                self._history.pop(0)

        notified = 0
        tasks = []

        for handler in handlers:
            try:
                if inspect.iscoroutinefunction(handler):
                    tasks.append(handler(event))
                else:
                    handler(event)
                    notified += 1
            except Exception as e:
                logger.error(
                    "EventBus async: erro no handler '{fn}': {err}",
                    fn=handler.__name__, err=str(e)
                )

        if tasks:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            for result in results:
                if isinstance(result, Exception):
                    logger.error("EventBus async: erro em task: {err}", err=str(result))
                else:
                    notified += 1

        return notified

    # -------------------------------------------------------------------------
    # Utilitários
    # -------------------------------------------------------------------------

    def get_subscribers(self, event_name: str) -> list[str]:
        """
        Retorna nomes dos handlers inscritos em um evento.

        Args:
            event_name: Nome do evento.

        Returns:
            Lista de nomes de funções inscritas.
        """
        with self._lock:
            return [h.__name__ for h in self._handlers.get(event_name, [])]

    def get_all_events(self) -> list[str]:
        """Retorna todos os nomes de eventos com ao menos um subscriber."""
        with self._lock:
            return [name for name, handlers in self._handlers.items() if handlers]

    def get_history(self, event_name: str | None = None, limit: int = 20) -> list[Event]:
        """
        Retorna histórico de eventos publicados.

        Args:
            event_name: Filtrar por nome do evento. None retorna todos.
            limit: Número máximo de eventos retornados.

        Returns:
            Lista de eventos mais recentes.
        """
        with self._lock:
            history = list(self._history)

        if event_name:
            history = [e for e in history if e.name == event_name]

        return history[-limit:]

    def clear_all_subscribers(self) -> None:
        """Remove todos os subscribers de todos os eventos. Use com cuidado."""
        with self._lock:
            self._handlers.clear()
        logger.warning("EventBus: todos os subscribers removidos")

    def stats(self) -> dict[str, Any]:
        """Retorna estatísticas do barramento."""
        with self._lock:
            return {
                "total_events_registered": len(self._handlers),
                "total_handlers": sum(len(h) for h in self._handlers.values()),
                "history_count": len(self._history),
                "events": {
                    name: len(handlers)
                    for name, handlers in self._handlers.items()
                    if handlers
                },
            }


# ---------------------------------------------------------------------------
# Constantes de Nomes de Eventos
# ---------------------------------------------------------------------------


class Events:
    """
    Constantes para nomes de eventos padronizados.
    Use sempre estas constantes em vez de strings literais.

    Evita erros de digitação e facilita refactoring.
    """

    # Aeronaves
    AIRCRAFT_UPDATED = "aircraft.updated"
    AIRCRAFT_ERROR = "aircraft.error"

    # ISS
    ISS_POSITION_UPDATED = "iss.position_updated"
    ISS_ERROR = "iss.error"

    # Clima
    WEATHER_UPDATED = "weather.updated"
    WEATHER_ERROR = "weather.error"

    # Lançamentos
    LAUNCH_UPDATED = "launch.updated"
    LAUNCH_ERROR = "launch.error"

    # Lua e Astronomia
    MOON_UPDATED = "moon.updated"
    SOLAR_SYSTEM_UPDATED = "solar_system.updated"

    # NASA
    NASA_APOD_UPDATED = "nasa.apod_updated"
    NASA_ERROR = "nasa.error"

    # Módulos
    MODULE_ENABLED = "module.enabled"
    MODULE_DISABLED = "module.disabled"

    # Scheduler
    SCHEDULER_TICK = "scheduler.tick"
    SCHEDULER_STARTED = "scheduler.started"
    SCHEDULER_STOPPED = "scheduler.stopped"

    # Sistema
    APP_STARTED = "app.started"
    APP_STOPPING = "app.stopping"
    ERROR_API = "error.api"
    ERROR_CRITICAL = "error.critical"


# ---------------------------------------------------------------------------
# Singleton Global
# ---------------------------------------------------------------------------

event_bus: EventBus = EventBus()
