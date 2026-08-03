# AeroTracker Core — Modules Specification

> Version 1.0 | 12 independent navigation modules

---

## Navigation Architecture

```
AppLayout
├── Sidebar (persistent navigation)
├── Toolbar (context actions)
├── Content Area (routed pages)
└── StatusBar (global status)
```

Each module is an **independent page** with its own:
- Zustand slice
- TanStack Query hooks
- WebSocket subscription (if real-time)
- Instrument components

---

## Module Index

| ID | Path | Icon | Data Source | Realtime |
|---|---|---|---|---|
| `dashboard` | `/` | LayoutDashboard | Aggregated | ✅ WS |
| `radar` | `/radar` | Radar | OpenSky | ✅ WS |
| `flights` | `/flights` | Plane | FlightAware / OpenSky | ✅ WS |
| `weather` | `/weather` | Cloud | OpenWeatherMap | Polling |
| `clock` | `/clock` | Clock | System | Timer |
| `iss` | `/iss` | Satellite | WhereTheISS | ✅ WS |
| `moon` | `/moon` | Moon | Ephemeris calc | Polling |
| `solar-system` | `/solar-system` | Globe | NASA / Ephemeris | Polling |
| `satellites` | `/satellites` | Radio | N2YO / CelesTrak | Polling |
| `launches` | `/launches` | Rocket | LaunchLibrary 2 | Polling |
| `settings` | `/settings` | Settings | Local config | — |
| `diagnostics` | `/diagnostics` | Activity | System internals | ✅ WS |

---

## Module Specifications

### DASHBOARD
**Purpose**: Mission control overview — key metrics from all active modules.

**Layout**: `WidgetGrid` with 4–6 `WidgetCard` instances.

**Widgets**:
- `AircraftCard` — count + speed of nearest aircraft
- `WeatherCard` — temperature, wind, flight category (VFR/IFR)
- `ClockWidget` — UTC + local time, stopwatch
- `ISSWidget` — current position, altitude, visibility
- `LaunchCard` — next launch countdown
- `SystemStatus` — module health indicators

**Data**: Aggregated from all stores. No direct API calls.

---

### RADAR
**Purpose**: Live ATC-style radar display of aircraft within 10km of GRU.

**Layout**: `RadarMap` (main, 70% width) + aircraft list (30% width).

**Components**:
- `RadarMap` — SVG/Canvas, animated sweep, range rings, blips
- `AircraftCard` — callsign, altitude, speed, heading per aircraft
- `Compass` — heading reference
- `WidgetCard` — stats (total, airborne, on-ground)

**Realtime**: WebSocket `ws/aircraft` → `aircraft.store`

**Update rate**: 3 seconds

---

### FLIGHTS
**Purpose**: Track individual scheduled flights by callsign.

**Layout**: Left panel (input + schedule) + center `FlightMap` + right metrics.

**Components**:
- `FlightMap` — route arc ICN→SFO style with progress indicator
- `MetricCard` — altitude, speed, distance, ETA
- `Timeline` — departure, current position, arrival
- `AircraftCard` — aircraft details

**State**: Managed in `aircraft.store` → `trackedFlight` slice.

---

### WEATHER
**Purpose**: Meteorological data at GRU station.

**Components**:
- `WeatherCard` — temperature, feels-like, humidity
- `Gauge` — wind speed/direction
- `MetricCard` — pressure, visibility
- `WidgetCard` — METAR raw string
- `StatusBadge` — VFR / MVFR / IFR / LIFR category

**Update rate**: 5 minutes

---

### CLOCK
**Purpose**: Multi-timezone clock panel.

**Components**:
- `ClockWidget` — analog/digital UTC clock
- `ClockWidget` — local timezone
- `ClockWidget` — up to 4 custom zones
- `Timeline` — event timeline with UTC markers

---

### ISS
**Purpose**: International Space Station real-time tracking.

**Layout**: `WorldMap` (center) + metrics panels.

**Components**:
- `WorldMap` — SVG orthographic projection with ISS position dot
- `MetricCard` — altitude, velocity, footprint
- `Compass` — orbital heading
- `StatusBadge` — daylight / penumbra / eclipse / night

**Realtime**: WebSocket `ws/iss` → `space.store`

**Update rate**: 5 seconds

---

### MOON
**Purpose**: Lunar phase, rise/set, illumination.

**Components**:
- `MoonWidget` — rendered moon phase (Canvas, CSS)
- `MetricCard` — illumination %, distance km, age days
- `Timeline` — rise, peak, set times
- `ClockWidget` — next full moon countdown

---

### SOLAR SYSTEM
**Purpose**: Planetary positions and ephemeris data.

**Components**:
- `PlanetWidget` (×8) — planet summary card
- `Gauge` — elongation, magnitude
- `MetricCard` — distance from Earth, angular diameter

---

### SATELLITES
**Purpose**: Satellite pass predictions over GRU.

**Components**:
- `WorldMap` — ground track visualization
- `Timeline` — upcoming passes with AOS/LOS times
- `MetricCard` — elevation, azimuth

---

### LAUNCHES
**Purpose**: Upcoming space launch schedule.

**Components**:
- `LaunchCard` (list) — vehicle, provider, pad, status, countdown
- `Timeline` — launch schedule
- `StatusBadge` — Go / TBD / Success / Failure / Hold

---

### SETTINGS
**Purpose**: Application configuration.

**Sections**:
- Location (lat/lon, timezone, search radius)
- API Keys (OpenSky, OpenWeather)
- Modules (enable/disable per module)
- Appearance (theme intensity)
- Notifications

---

### DIAGNOSTICS
**Purpose**: System health, module status, event log.

**Components**:
- Module status table (active, last update, error count)
- Event log (last 100 EventBus events)
- Cache stats (hit rate, size)
- WebSocket connection status

**Realtime**: WebSocket `ws/system`

---

## Module Communication Rules

1. Modules **never import from each other**
2. All shared data flows through **Zustand stores**
3. Server data fetched only through **TanStack Query hooks**
4. WebSocket subscriptions set up in **page-level components** via custom hooks
5. Stores are updated by hooks — components are **read-only consumers**
