# AeroTracker Core — Design System

> Version 1.0 | Dark Aerospace Theme
> Inspired by: Glass Cockpit · Mission Control · Radar ATC

---

## 1. Philosophy

- **No hardcoded colors** — only design tokens
- **No inline styles** — Tailwind utilities only (exceptions: Canvas/WebGL)
- **60 FPS animations** — GPU-accelerated transforms only
- **Professional instrument aesthetic** — not a dashboard, but a cockpit panel
- **Negative space** — less is more; information density is deliberate

---

## 2. Color Tokens

All colors defined in `src/design-system/tokens.ts`.

### Background Hierarchy
```
bg-base      #050608   ← Application background (deep black)
bg-panel     #0C0E12   ← Panel / sidebar background
bg-card      #131720   ← Widget card surface
bg-card-alt  #181D25   ← Alternate card (hover states)
bg-input     #0B0E14   ← Input field background
bg-overlay   rgba(5,6,8,0.85) ← Modal backdrop
```

### Borders
```
border-subtle   #1A1F2B   ← Default card borders
border-default  #242C3A   ← Focused / active borders
border-accent   rgba(71,243,160,0.3) ← Green accent border
```

### Primary Palette
```
primary         #47F3A0   ← Emerald green — active, positive, live
primary-dim     #2BB87A   ← Dimmed primary
primary-bg      #0A1F14   ← Primary background tint
```

### Secondary Palette
```
secondary       #33A8FF   ← Neon blue — informational, links
secondary-dim   #1B6FCC
secondary-bg    #091628
```

### Semantic Colors
```
text-primary    #FFFFFF   ← Main readable text
text-secondary  #B0BAC8   ← Labels, subtitles
text-muted      #5A6475   ← Disabled, timestamps
text-code       #7EC8E3   ← Monospace values (coordinates, codes)

attention       #FFC857   ← Orange — warnings, attention
danger          #FF5D5D   ← Red — errors, alerts, collisions
danger-bg       #1F0A0A   ← Red background tint

cyan            #00D4FF   ← Radar sweep, highlights
```

### Radar-specific
```
radar-bg        #020A06   ← Radar display background
radar-ring      rgba(0,212,255,0.15)  ← Range rings
radar-sweep     rgba(0,212,255,0.8)   ← Sweep line
radar-blip      #47F3A0   ← Airborne aircraft blip
radar-ground    #FFC857   ← Ground traffic blip
```

---

## 3. Typography

```
font-display   "Outfit", sans-serif      ← Titles, large metrics
font-body      "Inter", sans-serif       ← Body text, labels
font-mono      "JetBrains Mono", mono    ← Coordinates, codes, callsigns
```

### Scale (rem-based)
```
text-2xs   0.625rem  / 10px   ← Timestamps, tiny labels
text-xs    0.75rem   / 12px   ← Captions, metadata
text-sm    0.875rem  / 14px   ← Secondary text
text-base  1rem      / 16px   ← Body text
text-lg    1.125rem  / 18px   ← Card titles
text-xl    1.25rem   / 20px   ← Section headers
text-2xl   1.5rem    / 24px   ← Page titles
text-3xl   2rem      / 32px   ← Large metrics
text-5xl   3.5rem    / 56px   ← Hero metrics (altitude, speed)
```

---

## 4. Spacing

```
xs    4px    ← Tight spacing (icon gap)
sm    8px    ← Small padding (badge)
md    12px   ← Standard padding
lg    16px   ← Card padding
xl    24px   ← Section margin
2xl   32px   ← Large separation
3xl   48px   ← Page margin
```

---

## 5. Border Radius

```
radius-none   0px
radius-sm     4px    ← Inputs, small elements
radius-md     8px    ← Buttons, badges
radius-lg     12px   ← Cards, panels
radius-xl     16px   ← Modals, widgets
radius-full   9999px ← Pills, circular elements
```

---

## 6. Shadows & Glow

```
shadow-card     0 2px 12px rgba(0,0,0,0.5)
shadow-modal    0 8px 40px rgba(0,0,0,0.8)
glow-primary    0 0 12px rgba(71,243,160,0.3)
glow-secondary  0 0 12px rgba(51,168,255,0.3)
glow-danger     0 0 12px rgba(255,93,93,0.3)
```

---

## 7. Animation Tokens

All durations and easing defined in `src/design-system/animations.ts`.

```
duration-fast     150ms
duration-normal   250ms
duration-slow     400ms
duration-crawl    800ms

ease-out     cubic-bezier(0.16, 1, 0.3, 1)
ease-in-out  cubic-bezier(0.87, 0, 0.13, 1)
```

### Named Variants (Framer Motion)
```
fadeIn       opacity: 0 → 1
fadeOut      opacity: 1 → 0
slideLeft    x: -20 → 0, opacity: 0 → 1
slideRight   x:  20 → 0, opacity: 0 → 1
slideUp      y:  16 → 0, opacity: 0 → 1
scaleIn      scale: 0.95 → 1, opacity: 0 → 1
```

---

## 8. Icons

All icons from **Lucide Icons** (`lucide-react`).

Preferred icons by domain:
```
Aircraft   → Plane, PlaneLanding, PlaneOff
Radar      → Radar, Radio, Wifi
Weather    → Cloud, CloudRain, Wind, Thermometer
ISS        → Satellite, Orbit, Globe
Launches   → Rocket, Flame
Moon       → Moon, Eclipse
Clock      → Clock, Timer, AlarmClock
Settings   → Settings, Sliders, Wrench
Alert      → AlertTriangle, AlertCircle, Info
Connection → Wifi, WifiOff, Activity
```

### Usage
```tsx
import { Plane, Radar } from 'lucide-react'

// Always use fixed sizes — never inherit text size
<Plane size={16} className="text-primary" />
```

---

## 9. Component Tokens Reference

```ts
// tokens.ts
export const tokens = {
  colors: {
    bgBase: '#050608',
    bgPanel: '#0C0E12',
    bgCard: '#131720',
    primary: '#47F3A0',
    secondary: '#33A8FF',
    danger: '#FF5D5D',
    attention: '#FFC857',
    textPrimary: '#FFFFFF',
    textSecondary: '#B0BAC8',
    textMuted: '#5A6475',
    border: '#1A1F2B',
    cyan: '#00D4FF',
  },
  spacing: { xs: 4, sm: 8, md: 12, lg: 16, xl: 24 },
  radius: { sm: 4, md: 8, lg: 12, xl: 16 },
  fonts: {
    display: '"Outfit", sans-serif',
    body: '"Inter", sans-serif',
    mono: '"JetBrains Mono", monospace',
  },
} as const
```

---

## 10. Do / Don't

| ✅ Do | ❌ Don't |
|---|---|
| Use token colors via Tailwind classes | Use `#fff`, `red`, `rgb()` inline |
| Use `font-mono` for all coordinates | Mix font families ad-hoc |
| Use semantic color names (primary, danger) | Use aesthetic descriptions (green, blue) |
| Animate with transform/opacity only | Animate width/height/top/left |
| Use `motion.div` for animated elements | Use CSS `transition` on `opacity` changes |
| Group related info spatially | Scatter metrics across the screen |
| Show loading skeleton states | Show blank / empty views |
