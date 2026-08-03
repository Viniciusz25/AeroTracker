# AeroTracker Core — API Specification

> Version 2.0 | Base URL: `http://localhost:8000/api/v1`
> WebSocket Base: `ws://localhost:8000`

---

## Authentication

Phase 1: No authentication (local desktop app).
Phase 2: Bearer token via `Authorization: Bearer <token>` header.

---

## REST Endpoints

### System

#### `GET /health`
Returns application health and module status.

**Response 200**
```json
{
  "status": "ok",
  "version": "2.0.0",
  "uptime_seconds": 3600,
  "modules": {
    "aircraft": { "active": true, "last_updated": "2026-08-03T14:00:00Z" },
    "weather":  { "active": true, "last_updated": "2026-08-03T13:55:00Z" },
    "iss":      { "active": true, "last_updated": "2026-08-03T14:00:05Z" },
    "launch":   { "active": true, "last_updated": "2026-08-03T13:00:00Z" },
    "nasa":     { "active": true, "last_updated": "2026-08-03T12:00:00Z" }
  }
}
```

---

### Aircraft

#### `GET /aircraft`
Returns live aircraft snapshot within the configured bounding box.

**Query Parameters**
| Param | Type | Default | Description |
|---|---|---|---|
| `lat` | float | -23.4356 | Center latitude |
| `lon` | float | -46.4731 | Center longitude |
| `radius_km` | float | 10 | Search radius in km |

**Response 200**
```json
{
  "total_count": 8,
  "airborne_count": 7,
  "on_ground_count": 1,
  "query_time": 1785761255,
  "aircraft": [
    {
      "icao24": "e4953e",
      "callsign": "GLO1113",
      "origin_country": "Brazil",
      "position": { "latitude": -23.42, "longitude": -46.47 },
      "altitude": { "meters": 10668, "unit": "m" },
      "velocity": { "meters_per_second": 235.6, "unit": "m/s" },
      "heading": 278.5,
      "vertical_rate": -0.2,
      "on_ground": false,
      "category": "large",
      "last_contact": 1785761253
    }
  ]
}
```

**Response 204** — No data yet (service initializing)

---

### Weather

#### `GET /weather`
Returns current weather at the configured location.

**Response 200**
```json
{
  "location": "Guarulhos, BR",
  "temperature_c": 18.5,
  "feels_like_c": 16.2,
  "humidity_pct": 72,
  "pressure_hpa": 1018,
  "wind_speed_ms": 3.2,
  "wind_direction_deg": 145,
  "visibility_m": 10000,
  "condition": "Partly Cloudy",
  "icon_code": "02d",
  "metar": "SBGR 031400Z 14003KT 9999 FEW025 18/14 Q1018",
  "flight_category": "VFR",
  "updated_at": "2026-08-03T14:00:00Z"
}
```

---

### ISS

#### `GET /iss`
Returns current ISS position and orbital data.

**Response 200**
```json
{
  "name": "ISS",
  "norad_id": 25544,
  "position": { "latitude": -5.32, "longitude": -42.18 },
  "altitude_km": 421.3,
  "velocity_kmh": 27576,
  "visibility": "daylight",
  "footprint_km": 4543,
  "updated_at": "2026-08-03T14:00:02Z"
}
```

---

### Launches

#### `GET /launches`
Returns upcoming space launches.

**Query Parameters**
| Param | Type | Default | Description |
|---|---|---|---|
| `limit` | int | 10 | Max launches to return |
| `days` | int | 30 | Look-ahead window |

**Response 200**
```json
{
  "launches": [
    {
      "id": "starlink-g10-23",
      "name": "Starlink Group 10-23",
      "vehicle": "Falcon 9",
      "provider": "SpaceX",
      "pad": "SLC-40, Cape Canaveral",
      "status": "Go",
      "net": "2026-08-05T04:30:00Z",
      "probability_pct": 85,
      "mission_type": "Communications"
    }
  ],
  "total": 8
}
```

---

### NASA

#### `GET /nasa/apod`
Returns NASA Astronomy Picture of the Day.

**Response 200**
```json
{
  "title": "Milky Way Over Atacama",
  "date": "2026-08-03",
  "explanation": "...",
  "url": "https://apod.nasa.gov/apod/image/...",
  "media_type": "image",
  "copyright": "ESO"
}
```

---

## WebSocket Channels

### `ws://localhost:8000/ws/aircraft`

Real-time aircraft position updates (every 3 seconds).

**Message format**
```json
{
  "event": "aircraft.updated",
  "timestamp": "2026-08-03T14:00:05Z",
  "source": "opensky",
  "data": { /* same as GET /aircraft */ }
}
```

---

### `ws://localhost:8000/ws/iss`

Real-time ISS position updates (every 5 seconds).

```json
{
  "event": "iss.updated",
  "timestamp": "2026-08-03T14:00:05Z",
  "source": "wheretheiss",
  "data": { /* same as GET /iss */ }
}
```

---

### `ws://localhost:8000/ws/system`

System events: module errors, rate limits, health changes.

```json
{
  "event": "module.error",
  "timestamp": "2026-08-03T14:00:05Z",
  "data": {
    "module": "launch",
    "error": "HTTP 429: Rate limit. Retry-After: 115s"
  }
}
```

---

## Error Codes

| Code | Meaning |
|---|---|
| `SERVICE_NOT_INITIALIZED` | Module hasn't fetched data yet |
| `UPSTREAM_RATE_LIMITED` | Upstream API returned 429 |
| `UPSTREAM_UNAVAILABLE` | Upstream API unreachable |
| `INVALID_PARAMETERS` | Bad query parameters |

---

## Versioning

API version is included in the URL path: `/api/v1/`.
Breaking changes will increment the version to `/api/v2/`.
Both versions are served simultaneously during transitions.
