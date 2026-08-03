# AeroTracker Core — Roadmap

> Version 1.0 | Migration from PySide6 to React + FastAPI Monorepo

---

## Version History

| Version | Description | Status |
|---|---|---|
| v1.0 | PySide6 desktop app (MVC, EventBus, OpenSky) | ✅ Complete |
| v2.0 | React + FastAPI monorepo | 🔄 In Progress |
| v3.0 | Tauri 2 native desktop + authentication | Planned |
| v4.0 | Multi-device sync + cloud backend | Planned |

---

## v2.0 Milestones

### PHASE 1 — Documentation ✅
- [x] ARCHITECTURE.md
- [x] FRONTEND_GUIDE.md
- [x] BACKEND_GUIDE.md
- [x] API_SPEC.md
- [x] DESIGN_SYSTEM.md
- [x] MODULES.md
- [x] ROADMAP.md

### PHASE 2 — Backend FastAPI
- [ ] FastAPI app with lifespan management
- [ ] CORS + WebSocket support
- [ ] 6 domain routers (aircraft, weather, ISS, launches, NASA, system)
- [ ] WebSocket connection manager
- [ ] EventBus → WebSocket bridge
- [ ] SQLite database + SQLAlchemy async
- [ ] Auto-generated OpenAPI spec (`/docs`)

**Deliverable**: `uvicorn backend.main:app` serves all endpoints.
**Gate**: `curl http://localhost:8000/api/v1/health` returns 200.

---

### PHASE 3 — Frontend Infrastructure
- [ ] Vite + React 19 + TypeScript scaffold
- [ ] Tailwind CSS v4 + design tokens
- [ ] 8 Zustand stores (domain-separated)
- [ ] TanStack Query provider
- [ ] React Router v6 with 12 routes
- [ ] Axios base client with interceptors
- [ ] Path aliases (@/, @atoms/, etc.)
- [ ] Framer Motion animation variants

**Deliverable**: `npm run dev` shows blank router with working navigation.
**Gate**: TypeScript compiles with 0 errors (`npm run typecheck`).

---

### PHASE 4 — Atoms & Molecules
- [ ] Button (primary, ghost, danger, icon)
- [ ] Badge (status, count, pill)
- [ ] Icon (Lucide wrapper with size/color props)
- [ ] Label (semantic text sizes)
- [ ] Separator (horizontal/vertical)
- [ ] MetricCard (value + label + trend)
- [ ] StatusBadge (color-coded status pill)
- [ ] NavItem (sidebar navigation entry)
- [ ] DataRow (label + value pair)

**Deliverable**: All atoms/molecules visible in dev sandbox page.

---

### PHASE 5 — Organisms & Layout
- [ ] Sidebar (navigation + module list + status)
- [ ] Toolbar (page title + actions)
- [ ] StatusBar (WS status + clock + health)
- [ ] WidgetCard (glassmorphism panel container)
- [ ] WidgetGrid (responsive widget layout)
- [ ] Dialog (modal with backdrop)
- [ ] Notification (toast system)
- [ ] CircularMenu (radial navigation overlay)
- [ ] AppLayout (compose all organisms)

**Deliverable**: Full layout visible with navigation working between placeholder pages.

---

### PHASE 6 — Aerospace Instruments
- [ ] RadarMap (SVG/Canvas, sweep animation, blips)
- [ ] WorldMap (SVG orthographic projection, ISS track)
- [ ] FlightMap (route arc, progress indicator, telemetry overlay)
- [ ] Compass (heading indicator, animated)
- [ ] Gauge (analog gauge, wind/speed/altitude)
- [ ] Timeline (horizontal event timeline)
- [ ] ClockWidget (analog + digital, multi-timezone)
- [ ] MoonWidget (phase visualization, Canvas)
- [ ] PlanetWidget (planet summary with icon)
- [ ] LaunchCard (countdown, vehicle, status)
- [ ] WeatherCard (temp, humidity, flight category)
- [ ] AircraftCard (callsign, altitude, speed, track)

**Deliverable**: All instruments render with mock data.

---

### PHASE 7 — Pages & Routing
- [ ] Dashboard (WidgetGrid with 6 cards)
- [ ] Radar (RadarMap + aircraft list)
- [ ] Flights (FlightMap + metrics + schedule)
- [ ] Weather (WeatherCard + Gauge + METAR)
- [ ] Clock (multi-zone ClockWidget)
- [ ] ISS (WorldMap + orbit metrics)
- [ ] Moon (MoonWidget + ephemeris)
- [ ] Solar System (PlanetWidget grid)
- [ ] Satellites (WorldMap + pass timeline)
- [ ] Launches (LaunchCard list + Timeline)
- [ ] Settings (config form)
- [ ] Diagnostics (health table + event log)
- [ ] Page transition animations (Framer Motion)

**Deliverable**: All pages navigable with static/mock data.

---

### PHASE 8 — Integration
- [ ] WebSocket hooks connected to FastAPI
- [ ] TanStack Query fetching all REST endpoints
- [ ] Zustand stores fed by real backend data
- [ ] Error states (rate limit banners, retry UI)
- [ ] Loading skeleton states
- [ ] Connection status indicator in StatusBar
- [ ] End-to-end test: aircraft positions visible on RadarMap from OpenSky

**Deliverable**: Full app running with live data from backend.

---

### PHASE 9 — Tauri 2 Desktop Shell
- [ ] Tauri 2 project scaffold
- [ ] FastAPI backend spawned as Tauri sidecar
- [ ] Native window chrome, tray icon
- [ ] Custom title bar (frameless window)
- [ ] System notifications (aircraft alerts)
- [ ] Updater configuration
- [ ] Windows `.exe` installer build

**Deliverable**: `npm run tauri build` produces installable `.exe`.

---

## v3.0 Planned Features

- User authentication (JWT / OAuth2)
- Flight alert notifications (configurable thresholds)
- Aircraft history replay (time-scrubber)
- Custom dashboard layout builder (drag-and-drop widgets)
- Multiple location profiles (not just GRU)
- Dark / Light theme toggle
- Export reports (PDF / CSV)

---

## v4.0 Planned Features

- Cloud sync across devices
- PostgreSQL backend
- Multi-user support
- REST API public access (rate-limited)
- Mobile companion app (React Native)
- Circular display firmware (ESP32-S3 sync via MQTT)

---

## Known Technical Debt (v1.0)

| Issue | Impact | Target |
|---|---|---|
| `tracker_controller.py` — hardcoded ICN→SFO route | Medium | v2.0 Phase 8 |
| `vector_map_widget.py` — removed class alias | Low | v2.0 Phase 2 |
| Launch model not JSON serializable | Low | v2.0 Phase 2 |
| PySide6 painter warnings on hover effects | Low | Retired in v2.0 |
| `radius_km=10` hardcoded in service | Medium | v2.0 Phase 3 (settings) |
