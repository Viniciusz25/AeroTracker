# AeroTracker Core — Frontend Guide

> Version 1.0 | Stack: React 19 + TypeScript + Vite + Tailwind CSS
> Location: `frontend/`

---

## 1. Stack

| Tool | Version | Purpose |
|---|---|---|
| React | 19 | UI framework |
| TypeScript | 5.x | Type safety |
| Vite | 5.x | Build + dev server |
| Tailwind CSS | 4.x | Utility-first styling |
| Framer Motion | 11.x | Animations |
| React Router | 6.x | Client-side routing |
| TanStack Query | 5.x | Server state management |
| Zustand | 4.x | Client state management |
| Lucide Icons | Latest | SVG icon library |
| Axios | Latest | HTTP client |

---

## 2. Project Structure

```
frontend/src/
├── main.tsx                 ← App entry point
├── App.tsx                  ← Root component + providers
├── design-system/
│   ├── tokens.ts            ← Design tokens (colors, spacing, radii)
│   ├── theme.ts             ← Dark theme definition
│   └── animations.ts       ← Framer Motion shared variants
├── components/
│   ├── atoms/               ← Button, Badge, Icon, Label, Separator
│   ├── molecules/           ← MetricCard, NavItem, DataRow, StatusBadge
│   ├── organisms/           ← Sidebar, Toolbar, WidgetCard, Dialog
│   └── instruments/         ← RadarMap, FlightMap, Compass, Gauge…
├── layouts/
│   └── AppLayout.tsx        ← Root layout (Sidebar + Toolbar + Content + StatusBar)
├── pages/                   ← One file per route
├── store/                   ← Zustand stores (one file per domain)
├── hooks/                   ← Custom React hooks
├── services/                ← API client + per-domain query functions
├── types/                   ← TypeScript interfaces
└── router/
    └── index.tsx            ← Route definitions
```

---

## 3. Component Rules

### Atomic Design Levels

```
atoms      → No dependencies on other components. Pure HTML + Tailwind.
molecules  → Compose atoms. No business logic.
organisms  → Compose molecules. May consume Zustand store (read-only).
pages      → Assemble organisms. Trigger TanStack Query hooks.
```

### File Template (component)

```tsx
// src/components/atoms/Button.tsx
import type { FC, ButtonHTMLAttributes } from 'react'
import { motion } from 'framer-motion'
import { tokens } from '@/design-system/tokens'

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'ghost' | 'danger'
  size?: 'sm' | 'md' | 'lg'
}

export const Button: FC<ButtonProps> = ({
  variant = 'primary',
  size = 'md',
  children,
  ...props
}) => {
  return (
    <motion.button
      whileTap={{ scale: 0.97 }}
      className={buttonVariants({ variant, size })}
      {...props}
    >
      {children}
    </motion.button>
  )
}
```

### Rules
- Every component has a **single named export** (no default exports)
- Props interfaces are always **explicitly typed** (no `any`)
- Styling uses only **Tailwind utility classes** referencing design tokens
- No `style={{}}` inline styles — exceptions only for computed values (e.g., Canvas)
- Max **300 lines** per file — split into sub-components if needed

---

## 4. State Management

### Zustand Store Template

```ts
// src/store/aircraft.store.ts
import { create } from 'zustand'
import type { AircraftState, AircraftList } from '@/types/aircraft.types'

interface AircraftStore {
  aircraftList: AircraftList | null
  selectedAircraft: AircraftState | null
  setAircraftList: (data: AircraftList) => void
  selectAircraft: (aircraft: AircraftState) => void
  clearSelection: () => void
}

export const useAircraftStore = create<AircraftStore>((set) => ({
  aircraftList: null,
  selectedAircraft: null,
  setAircraftList: (data) => set({ aircraftList: data }),
  selectAircraft: (aircraft) => set({ selectedAircraft: aircraft }),
  clearSelection: () => set({ selectedAircraft: null }),
}))
```

### Store → Component Pattern

```tsx
// pages/Radar.tsx
import { useAircraftStore } from '@/store/aircraft.store'
import { useAircraftQuery } from '@/hooks/useAircraft'

export const RadarPage: FC = () => {
  const { aircraftList } = useAircraftStore()
  useAircraftQuery() // populates the store via WebSocket
  return <RadarMap aircraft={aircraftList?.aircraft ?? []} />
}
```

---

## 5. Data Fetching

### TanStack Query (REST)

```ts
// hooks/useWeather.ts
import { useQuery } from '@tanstack/react-query'
import { fetchWeather } from '@/services/weather.service'
import { useWeatherStore } from '@/store/weather.store'

export function useWeatherQuery() {
  const { setWeather } = useWeatherStore()

  return useQuery({
    queryKey: ['weather'],
    queryFn: async () => {
      const data = await fetchWeather()
      setWeather(data)
      return data
    },
    staleTime: 5 * 60 * 1000, // 5 minutes
    refetchInterval: 5 * 60 * 1000,
  })
}
```

### WebSocket (real-time)

```ts
// hooks/useWebSocket.ts
import { useEffect } from 'react'
import { useConnectionStore } from '@/store/connection.store'

export function useWebSocket(channel: string, onMessage: (data: unknown) => void) {
  const { setConnected } = useConnectionStore()

  useEffect(() => {
    const ws = new WebSocket(`ws://localhost:8000/ws/${channel}`)
    ws.onopen = () => setConnected(channel, true)
    ws.onclose = () => setConnected(channel, false)
    ws.onmessage = (e) => onMessage(JSON.parse(e.data))
    return () => ws.close()
  }, [channel])
}
```

---

## 6. Animations (Framer Motion)

Use shared variants from `design-system/animations.ts`. Never write one-off animations.

```ts
// design-system/animations.ts
export const fadeIn = {
  initial: { opacity: 0 },
  animate: { opacity: 1 },
  exit: { opacity: 0 },
  transition: { duration: 0.2 },
}

export const slideFromLeft = {
  initial: { x: -20, opacity: 0 },
  animate: { x: 0, opacity: 1 },
  exit: { x: -20, opacity: 0 },
  transition: { duration: 0.25, ease: 'easeOut' },
}
```

```tsx
// Usage
import { motion } from 'framer-motion'
import { fadeIn } from '@/design-system/animations'

<motion.div {...fadeIn}>
  <MetricCard ... />
</motion.div>
```

---

## 7. Routing

```tsx
// router/index.tsx
import { createBrowserRouter } from 'react-router-dom'
import { AppLayout } from '@/layouts/AppLayout'
import { Dashboard } from '@/pages/Dashboard'
import { Radar } from '@/pages/Radar'
// ...

export const router = createBrowserRouter([
  {
    path: '/',
    element: <AppLayout />,
    children: [
      { index: true, element: <Dashboard /> },
      { path: 'radar', element: <Radar /> },
      { path: 'flights', element: <Flights /> },
      { path: 'weather', element: <Weather /> },
      // ...
    ],
  },
])
```

---

## 8. TypeScript Rules

- **Strict mode** enabled (`"strict": true` in tsconfig)
- No `any` — use `unknown` + type narrowing if needed
- All component props have explicit interfaces
- All API responses have typed interfaces in `src/types/`
- Use `satisfies` operator for type-checked literals

---

## 9. Available Scripts

```bash
# Inside frontend/
npm run dev          # Vite dev server (port 5173)
npm run build        # Production build
npm run preview      # Preview production build
npm run typecheck    # tsc --noEmit
npm run lint         # ESLint
npm test             # Vitest unit tests
```

---

## 10. Path Aliases

Configured in `vite.config.ts` and `tsconfig.json`:

```
@/         → src/
@atoms/    → src/components/atoms/
@molecules → src/components/molecules/
@organisms → src/components/organisms/
@instruments → src/components/instruments/
@store/    → src/store/
@hooks/    → src/hooks/
@types/    → src/types/
@ds/       → src/design-system/
```
