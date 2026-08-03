# AeroTracker Core — Architecture

> Version 1.0 | Lead Architect: AeroTracker Core Team
> Last updated: 2026-08-03

---

## 1. Overview

AeroTracker Core is a modular aerospace monitoring platform.
It tracks aircraft, satellites, the ISS, weather, lunar phases, planetary positions
and space launches in real time.

The architecture is built on three independent layers:

```
┌─────────────────────────────────────────────────────┐
│  Desktop Shell  (Tauri 2 — Rust + WebView)          │
├─────────────────────────────────────────────────────┤
│  Frontend       (React 19 + TypeScript + Vite)      │
├─────────────────────────────────────────────────────┤
│  Communication  (REST + WebSocket over FastAPI)     │
├─────────────────────────────────────────────────────┤
│  Backend        (Python 3.13 + FastAPI + AsyncIO)   │
├─────────────────────────────────────────────────────┤
│  External APIs  (OpenSky, NASA, Weather, Launch…)   │
└─────────────────────────────────────────────────────┘
```

No layer communicates with external APIs directly except the **Backend**.

---

## 2. Repository Structure (Monorepo)

```
aerotracker/
├── backend/          ← FastAPI application (wraps existing Python services)
├── frontend/         ← React 19 + Vite + TypeScript SPA
├── shared/           ← OpenAPI schema, shared type definitions
├── docs/             ← Architecture documents (this file and siblings)
├── assets/           ← Brand assets, icons, SVGs
├── firmware/         ← ESP32-S3 firmware (AMOLED device twin)
│
│── [preserved Python core]
├── api/              ← External API clients (OpenSky, NASA, etc.)
├── services/         ← Business services (Aircraft, ISS, Weather…)
├── cache/            ← CacheManager with TTL
├── core/             ← EventBus, ModuleManager, App bootstrap
├── models/           ← Pydantic domain models
├── scheduler/        ← JobScheduler (background polling)
├── storage/          ← LocalStorage (JSON persistence)
└── config/           ← AppSettings, modules.toml
```

---

## 3. Data Flow

### REST Request Flow

```
User action in React component
  → TanStack Query (useQuery / useMutation)
  → api.client.ts (Axios)
  → FastAPI Router (backend/)
  → Service (services/)
  → API Client (api/)
  → External API
  → Pydantic Model
  → JSON response
  → TanStack Query cache
  → Zustand store update
  → React component re-render
```

### WebSocket Real-time Flow

```
JobScheduler triggers service.update()
  → Service fetches from External API
  → EventBus publishes event (e.g., "aircraft.updated")
  → WebSocket broadcaster receives event
  → Pushes JSON payload to all connected clients
  → useWebSocket() hook in React receives message
  → Zustand store updated
  → Components re-render at 60 FPS
```

---

## 4. Backend Architecture

The backend is built on the **existing Python core** (preserved 100%) with a
FastAPI layer added on top.

### Existing Core (unchanged)
| Module | Responsibility |
|---|---|
| `core/event_bus.py` | Publish/subscribe event system |
| `core/module_manager.py` | Module lifecycle (enable/disable/error) |
| `scheduler/job_scheduler.py` | Periodic background jobs |
| `cache/cache_manager.py` | In-memory cache with TTL |
| `services/base_service.py` | BaseService with retry and fallback |
| `models/` | Pydantic domain models (Aircraft, ISS, Weather…) |

### New FastAPI Layer
| Module | Responsibility |
|---|---|
| `backend/main.py` | FastAPI app, CORS, startup, lifespan |
| `backend/routers/` | HTTP endpoints per domain |
| `backend/websocket/manager.py` | WebSocket connection pool |
| `backend/websocket/events.py` | Event → WebSocket bridge |
| `backend/database/` | SQLAlchemy async ORM |

---

## 5. Frontend Architecture

Follows **Atomic Design** for components and **Clean Architecture** for layers.

```
pages/          ← Route-level components (assemble organisms)
  └─ organisms/ ← Complex UI sections (Sidebar, RadarMap, WidgetGrid)
      └─ molecules/ ← Reusable compound components (MetricCard, NavItem)
          └─ atoms/ ← Primitive UI elements (Button, Badge, Icon)
```

State is managed by **Zustand** (8 independent stores, no cross-store imports).
Server state is managed by **TanStack Query** (caching, invalidation, optimistic updates).

---

## 6. Communication Protocol

### REST Endpoints (TanStack Query)
- Suitable for: initial data load, user-triggered actions, settings
- Cache strategy: stale-while-revalidate with configurable TTL per resource

### WebSocket Channels
- `ws://localhost:8000/ws/aircraft` — live aircraft positions
- `ws://localhost:8000/ws/iss` — ISS position (5s interval)
- `ws://localhost:8000/ws/system` — module health, errors

### Message Format
```json
{
  "event": "aircraft.updated",
  "timestamp": "2026-08-03T14:00:00Z",
  "source": "opensky",
  "data": { ... }
}
```

---

## 7. Design Principles

1. **No business logic in the frontend** — React components are pure views
2. **Single source of truth** — Zustand stores, no prop drilling
3. **Composable components** — composition over inheritance
4. **Type safety** — TypeScript strict mode, no `any`
5. **Token-based design** — no hardcoded colors or sizes
6. **300-line limit** — no file exceeds 300 lines
7. **SOLID** — each module has a single, well-defined responsibility

---

## 8. Technology Decisions

| Decision | Choice | Rationale |
|---|---|---|
| Frontend framework | React 19 | Concurrent rendering, RSC-ready |
| Build tool | Vite 5 | Instant HMR, ESM-first |
| Styling | Tailwind CSS v4 | Token-driven, no runtime |
| Animation | Framer Motion | Declarative, GPU-accelerated |
| State (client) | Zustand | Minimal, composable, no boilerplate |
| State (server) | TanStack Query | Cache, invalidation, background refetch |
| Routing | React Router v6 | File-based optional, declarative |
| Desktop shell | Tauri 2 | Rust security, native APIs, small binary |
| Backend runtime | Python 3.13 | Existing codebase, async mature |
| API framework | FastAPI | Async, Pydantic-native, OpenAPI auto-gen |
| Database (dev) | SQLite | Zero-setup, file-based |
| Database (prod) | PostgreSQL | Scalable, JSONB support |

---

## 9. Security

- CORS restricted to `localhost` in development
- Tauri CSP enforced in production
- No API keys exposed to frontend
- All external API calls made server-side only
- WebSocket authentication via token header (Phase 8)

---

## 10. References

- [FastAPI Docs](https://fastapi.tiangolo.com)
- [React 19 Docs](https://react.dev)
- [Tauri 2 Docs](https://tauri.app)
- [Zustand](https://zustand-demo.pmnd.rs)
- [TanStack Query](https://tanstack.com/query)
- [Framer Motion](https://www.framer.com/motion)
