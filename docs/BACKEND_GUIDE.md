# AeroTracker Core — Backend Guide

> Version 1.0 | Stack: Python 3.13 + FastAPI + AsyncIO
> Location: `backend/`

---

## 1. Philosophy

The backend is the **single source of truth** for all domain data.
No business logic exists in the frontend.

All existing Python modules (`api/`, `services/`, `cache/`, `core/`, `scheduler/`)
are preserved unchanged. The `backend/` layer simply **exposes** them via HTTP and WebSocket.

---

## 2. Stack

| Tool | Version | Purpose |
|---|---|---|
| Python | 3.13 | Runtime |
| FastAPI | 0.115.x | HTTP + WebSocket framework |
| Pydantic | 2.x | Data validation + serialization |
| SQLAlchemy | 2.x (async) | ORM + migrations |
| Uvicorn | Latest | ASGI server |
| Alembic | Latest | Database migrations |
| aiosqlite | Latest | Async SQLite driver (dev) |
| asyncpg | Latest | Async PostgreSQL driver (prod) |

---

## 3. Directory Structure

```
backend/
├── main.py                  ← FastAPI app, lifespan, CORS, WebSocket mount
├── routers/
│   ├── __init__.py
│   ├── aircraft.py          ← GET /api/v1/aircraft
│   ├── weather.py           ← GET /api/v1/weather
│   ├── iss.py               ← GET /api/v1/iss
│   ├── launches.py          ← GET /api/v1/launches
│   ├── nasa.py              ← GET /api/v1/nasa/apod
│   └── system.py            ← GET /api/v1/health, GET /api/v1/modules
├── websocket/
│   ├── __init__.py
│   ├── manager.py           ← ConnectionManager (connect, disconnect, broadcast)
│   └── events.py            ← EventBus → WebSocket bridge
└── database/
    ├── __init__.py
    ├── engine.py            ← Async SQLAlchemy engine
    ├── models.py            ← ORM table definitions
    └── migrations/          ← Alembic migration scripts
```

---

## 4. FastAPI App Entry Point

```python
# backend/main.py
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core.app import AeroTrackerApp
from scheduler.job_scheduler import job_scheduler
from services.aircraft_service import AircraftService
from backend.routers import aircraft, weather, iss, launches, nasa, system
from backend.websocket.events import start_event_bridge


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    core_app = AeroTrackerApp()
    core_app.initialize()
    job_scheduler.start()
    start_event_bridge()
    yield
    # Shutdown
    job_scheduler.stop()
    core_app.shutdown()


app = FastAPI(
    title="AeroTracker Core API",
    version="2.0.0",
    lifespan=lifespan,
)

app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:5173"])
app.include_router(aircraft.router, prefix="/api/v1")
app.include_router(weather.router, prefix="/api/v1")
app.include_router(iss.router, prefix="/api/v1")
app.include_router(launches.router, prefix="/api/v1")
app.include_router(nasa.router, prefix="/api/v1")
app.include_router(system.router, prefix="/api/v1")
```

---

## 5. Router Pattern

```python
# backend/routers/aircraft.py
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from services.aircraft_service import AircraftService
from backend.websocket.manager import ws_manager

router = APIRouter(tags=["aircraft"])
_service = AircraftService()


@router.get("/aircraft")
async def get_aircraft():
    """Returns the latest aircraft snapshot."""
    data = _service.last_data
    if data is None:
        return {"aircraft": [], "total": 0}
    return data.model_dump()


@router.websocket("/ws/aircraft")
async def ws_aircraft(websocket: WebSocket):
    await ws_manager.connect(websocket, channel="aircraft")
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket, channel="aircraft")
```

---

## 6. WebSocket Manager

```python
# backend/websocket/manager.py
from collections import defaultdict
from fastapi import WebSocket
import json


class ConnectionManager:
    def __init__(self):
        self._channels: dict[str, list[WebSocket]] = defaultdict(list)

    async def connect(self, ws: WebSocket, channel: str) -> None:
        await ws.accept()
        self._channels[channel].append(ws)

    def disconnect(self, ws: WebSocket, channel: str) -> None:
        self._channels[channel].remove(ws)

    async def broadcast(self, channel: str, payload: dict) -> None:
        message = json.dumps(payload)
        for ws in list(self._channels[channel]):
            try:
                await ws.send_text(message)
            except Exception:
                self._channels[channel].remove(ws)


ws_manager = ConnectionManager()
```

---

## 7. EventBus → WebSocket Bridge

```python
# backend/websocket/events.py
from core.event_bus import event_bus, Events
from backend.websocket.manager import ws_manager
import asyncio


def start_event_bridge():
    """Subscribes to Python EventBus and broadcasts to WebSocket channels."""

    def _on_aircraft(event):
        if event.data:
            asyncio.create_task(
                ws_manager.broadcast("aircraft", {
                    "event": "aircraft.updated",
                    "data": event.data.model_dump(),
                })
            )

    def _on_iss(event):
        if event.data:
            asyncio.create_task(
                ws_manager.broadcast("iss", {
                    "event": "iss.updated",
                    "data": event.data.model_dump(),
                })
            )

    event_bus.subscribe(Events.AIRCRAFT_UPDATED, _on_aircraft)
    event_bus.subscribe(Events.ISS_POSITION_UPDATED, _on_iss)
```

---

## 8. API Response Conventions

All responses follow this structure:

```json
// Success
{
  "status": "ok",
  "timestamp": "2026-08-03T14:00:00Z",
  "data": { ... }
}

// Error
{
  "status": "error",
  "code": "SERVICE_UNAVAILABLE",
  "message": "OpenSky API rate limit exceeded",
  "retry_after": 115
}
```

### HTTP Status Codes
| Code | Meaning |
|---|---|
| 200 | Success |
| 204 | Success, no data yet (service not initialized) |
| 429 | Rate limited by upstream API |
| 503 | Service temporarily unavailable |

---

## 9. Database (SQLAlchemy Async)

```python
# backend/database/engine.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "sqlite+aiosqlite:///./aerotracker.db"

engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
```

---

## 10. Running the Backend

```bash
# Install dependencies
pip install fastapi uvicorn[standard] aiosqlite sqlalchemy alembic

# Development (hot reload)
uvicorn backend.main:app --reload --port 8000

# Production
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --workers 1
```

Access interactive docs at: `http://localhost:8000/docs`

---

## 11. Environment Variables

See `.env.example` for full reference. Key variables:

```
OPENSKY_USERNAME=
OPENSKY_PASSWORD=
OPENWEATHER_API_KEY=
DATABASE_URL=sqlite+aiosqlite:///./aerotracker.db
BACKEND_CORS_ORIGINS=http://localhost:5173
```
