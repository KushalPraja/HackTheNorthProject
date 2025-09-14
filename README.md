# HackThe North — AR Robotics & Sensing Projects

This repository contains prototype code and Lens Studio assets for three related AR projects: a healthcare robot-arm assist (reverse arm), an AI trash-detection & automatic pickup demo (giant arm + AR spectacles), and simple environmental sensors (air quality + noise pollution). The README below explains each idea, quick copyable descriptions to share/copy, how to run the backend, and the on-disk file structure for the important folders (`Backend/` and `Lens_Project/`).

## Project summaries (copy-friendly)

- Healthcare — Reverse Arm (doctor using robot arms in AR)

  Copy this short description to share:

  "AR-assisted Reverse Arm: the system overlays a remote robotic arm in the doctor's AR view. The doctor uses natural hand gestures (pinch, target, grab) captured by Spectacles/Lens Studio — these gestures are sent to a backend which translates them to robot commands. The robot arm mirrors precise manipulation (hold, move, release) to assist with tasks such as instrument handing or simulated training. Low-latency streaming and a live dashboard enable monitoring and safety stop states."

- AI Trash Detector — Giant Arm with AR Spectacles

  Copy this short description:

  "AI Trash Detector + Giant Arm: Spectacles view highlights detected trash items in the scene using an onboard AI model (or remote inference). When trash is detected, a large robotic arm (simulated or real) is visually shown in AR picking the item up automatically. The system can toggle between automatic pickup and manual authoritative control via simple gestures. Useful for public-space demos showing robotics + AR coordination."

- Environmental Sensors — Air Quality & Noise Pollution

  Copy this short description:

  "Environmental Sensing: small sensor modules stream air quality (PM2.5, VOCs, CO2 proxy) and noise levels into the backend. Spectacles/Lens Studio overlays live sensor readings and heatmaps in AR so a user can see hotspots for pollution and noise in their environment. Alerts can be shown if thresholds are exceeded."

## What this repo contains (short)

- `Backend/` — Flask + Flask-SocketIO server that receives gesture and sensor events, broadcasts updates to dashboard clients, and contains a simple gesture simulator used for local testing.
- `Lens_Project/` — Lens Studio project files and TypeScript assets that implement the on-device AR logic, gesture capture, and network calls to the backend.

## Quickstart — Backend (local)

Prerequisites: Python 3.9+ and pip.

1. Create and activate a Python virtual environment (PowerShell example):

```powershell
python -m venv .venv; .\.venv\Scripts\Activate.ps1
```

2. Install dependencies (from `Backend/requirements.txt`):

```powershell
pip install -r Backend\requirements.txt
```

3. Run the server:

```powershell
python Backend\app.py
```

What the backend provides:

- HTTP health check: GET /health → {status: 'ok'}
- Gesture ingest endpoint: POST /api/gesture — receives JSON gesture payloads from Lens Studio or other clients
- WebSocket / Socket.IO: Real-time broadcast for gesture updates (used by `dashboard.html`)
- Dashboard: open http://localhost:5000/ to view `templates/dashboard.html` which shows live gestures, counts, and a chart

Testing with simulator:

```powershell
python Backend\gesture_simulator.py
```

This script connects to the Socket.IO server and emits synthetic gestures for testing.

## API shape / contract (gesture payload)

Typical JSON fields the backend expects (examples):

- type: string (e.g. `pinch_down`, `pinch_up`, `targeting`, `grab_begin`, `state_change`)
- hand: string (`left` or `right`)
- timestamp: ISO datetime string (backend attaches timestamp if missing)
- confidence, rayOrigin, rayDirection, isValid — optional fields depending on gesture

Error modes: backend returns 400 for missing JSON, 500 for server errors. Success returns {status: 'success'}.

Edge cases to consider when integrating:

- missing hand/type fields
- burst/large frequency of events (server keeps last 100 entries)
- network disconnects (Lens Studio or Spectacles should retry)

## File structure explanation — `Backend/`

Key files:

- `Backend/app.py` — main Flask + Flask-SocketIO server. Routes:

  - `/health` — simple health check
  - `/api/gesture` (POST) — receives gesture JSON and broadcasts via Socket.IO
  - `/` — serves the dashboard at `templates/dashboard.html`
  - Socket handlers: `gesture_data`, `get_gesture_history` and connection events
  - `process_gesture_for_robot()` — placeholder for mapping gestures to robot commands

- `Backend/gesture_simulator.py` — a Socket.IO client that emits randomized gesture events for testing. Use it to simulate real usage while developing the dashboard and robot mapping.
- `Backend/requirements.txt` — Python dependencies (Flask, flask-socketio, etc.)
- `Backend/templates/dashboard.html` — a small dashboard UI that connects to the Socket.IO server and displays real-time gestures and stats.

Notes:

- The backend stores recent gestures in-memory (variable `gesture_data`) and trims the list to the last 100 entries. In production you'd replace this with a persistent data store.

## File structure explanation — `Lens_Project/`

This folder contains the Lens Studio project and compiled TypeScript assets used on Spectacles or in Lens Studio previews. Important items in the project:

- `Lens_Project/Lens_Project.esproj` — Lens Studio project descriptor (project metadata)
- `Lens_Project/tsconfig.json`, `jsconfig.json` — TypeScript/JS project configuration used by Lens Studio's TypeScript tooling
- `Lens_Project/Assets/GestureController.ts` — primary TypeScript module that captures gestures, formats payloads, and sends them to the backend API or emits Socket.IO events. (This is the place to add mapping logic from gestures to robot commands or to the AI trash detector's control channel.)
- `Lens_Project/Assets/Device Camera Texture.deviceCameraTexture` — camera texture used by the project
- `Lens_Project/Assets/Render Target.renderTarget` — render target asset used by visualizations
- `Lens_Project/Packages/SpectaclesInteractionKit.lspkg` — package used to help interaction on Spectacles devices (may contain useful helpers for gestures and UI)
- `Lens_Project/Support/StudioLib.d.ts` — type declarations for Lens Studio runtime APIs

Notes and integration tips:

- If you want the Lens project to send gestures directly as HTTP POSTs, call the `/api/gesture` endpoint with JSON. If you prefer realtime UX, integrate a Socket.IO client (or a small WebSocket shim) in the TypeScript to push gestures and listen for updates.
- The `GestureController.ts` file (and the TypeScript-built results under `Cache/TypeScript/StoredResults`) are the place to wire up AR overlays (reverse arm visuals, giant arm, sensor HUDs) to the incoming/outgoing network events.

## Suggested next steps / improvements

- Add a reconnect/backoff strategy in the Lens TypeScript for network reliability.
- Swap in a small ML model (on-device or remote) for trash detection — show bounding boxes or a highlight in AR and send detection events to the backend.
- Add authentication and rate-limiting for the backend endpoints before deploying publicly.
- Replace in-memory gesture storage with a lightweight DB (SQLite/Postgres) for analytics and replay.

## Where to look in the code right now

- `Backend/app.py` — start here to understand server behavior and robot-mapping placeholder
- `Backend/gesture_simulator.py` — use this to simulate traffic to the server
- `Lens_Project/Assets/GestureController.ts` — edit this to change gesture capture and network behavior

---

If you'd like, I can also:

- add a short CONTRIBUTING.md with dev setup steps,
- wire up a minimal Dockerfile to containerize the backend, or
- create a small sample README snippet you can paste into Lens Studio's Project Description.

Tell me which of those you'd like next and I'll proceed.
