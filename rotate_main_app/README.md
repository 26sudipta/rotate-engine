# ROTATE — Climate-Resilient Crop Rotation Intelligence

A decision-support prototype built for **NASA Space Apps Challenge 2026**. ROTATE connects
historical climate patterns, current environmental conditions, and crop-rotation
characteristics into a single scenario-analysis view for coastal and delta farmland in
Bangladesh.

**This prototype currently runs on a demonstration dataset**, not live NASA Earth Observation
data. The architecture (see "Replacing mock data" below) is structured so a real data source
can be swapped in without changing the frontend or the API surface.

## Design

The interface follows a farm-themed design system: deep forest green and sunflower yellow on warm
cream, handwritten script headings (Sue Ellen Francisco), Work Sans / Nunito typography, torn-paper
section edges, grass-blade dividers, dashed-border cards and pill buttons with a yellow icon circle.
All artwork (logo, rotation emblem, hay-bale field, windmill line art) is original SVG. Fonts load
from Google Fonts, so an internet connection is needed to see them as designed.

## Pages

`/` Home · `/dashboard` · `/farm/:id` · `/historical` · `/strategies` · `/scenario` · `/results` ·
`/crops` (Crop Library) · `/methodology` (scoring, data roadmap, FAQ) · `/contact` · 404

## Project structure

```
rotate/
  client/     React + Vite frontend (Tailwind, React Router, Recharts, Leaflet, Framer Motion)
  server/     Express REST API serving the demonstration dataset
```

## Running locally

You need Node.js 18+ installed.

### 1. Start the API server

```bash
cd server
npm install
npm start          # listens on http://localhost:4000
```

### 2. Start the frontend

In a second terminal:

```bash
cd client
npm install
npm run dev         # opens on http://localhost:5173
```

The client reads the API base URL from `client/.env` (`VITE_API_URL`), which defaults to
`http://localhost:4000/api`.

### 3. Build for production

```bash
cd client
npm run build        # outputs client/dist
```

## API endpoints

| Method | Path                      | Description                                            |
| ------ | ------------------------- | -------------------------------------------------------|
| GET    | `/api/health`             | Service health check                                   |
| GET    | `/api/locations`          | List demonstration farm locations                      |
| GET    | `/api/locations/:id`      | Single location detail                                 |
| GET    | `/api/climate/:locationId`| Current (demo) climate conditions for a location        |
| GET    | `/api/historical/:locationId` | 40-year demonstration climate timeline + closest analog year |
| GET    | `/api/strategies`         | List example crop rotation strategies                  |
| GET    | `/api/strategies/ranked`  | Strategies ranked by priority weights (query params)    |
| POST   | `/api/analyze`            | Bundled climate + historical + ranked-strategy response for a location |
| POST   | `/api/scenario`           | Runs the deterministic What-If scenario model            |
| GET    | `/api/crops`              | Illustrative crop profiles (Crop Library)                |
| POST   | `/api/contact`            | Contact form (kept in server memory only, never emailed)  |

## Replacing mock data with real NASA data

All demonstration data lives under `server/data/`. Each file documents the shape a real
integration should preserve:

- `locations.data.js` — farm/location registry
- `climate.data.js` — current conditions (swap for NASA POWER / SMAP / GPM, etc.)
- `historical.data.js` — historical time series (swap for a real climate archive)
- `strategies.data.js` — crop rotation indicator profiles (swap for a validated agronomic model)

The scenario formula itself is isolated in `server/utils/scenarioModel.js` (mirrored on the
client in `client/src/utils/scenarioModel.js` for instant slider feedback) so it can be
replaced with a real scientific model without touching route or controller code.

## Scientific integrity note

Values labeled "Demonstration dataset" or "Prototype analysis" throughout the UI are
illustrative placeholders for this prototype. They are not NASA measurements, validated
historical climate findings, or scientifically validated crop recommendations.
