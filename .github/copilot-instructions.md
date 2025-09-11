# Copilot instructions for gdop

This file gives targeted, actionable guidance for AI coding agents working on this repo.

1) Big picture
- app.py: program entry — constructs a `simulation.Scenario()` and `presentation.MainWindow` (PyQt5) and runs the Qt event loop.
- presentation/: UI layer (PyQt5 + matplotlib). Main window is `presentation/mainwindow.py`. Tabs live under `presentation/tabs/`.
- simulation/: core domain model and algorithms (stations, measurements, geometry, GDOP calculations). See `simulation/scenario.py` for how a `Scenario` composes anchors, tags and measurements.
- data/: import and streaming helpers. `data/importer.py` expects CSVs in `workspace/` and JSON scenario descriptors. `data/streaming.py` provides a Streamer used by `Scenario.start_streaming(url)`.

2) Primary workflows (how to run & debug)
- Run GUI locally: create a virtualenv, install `requirements.txt`, then `python app.py`.
- Quick headless test: create a `simulation.Scenario()` in a REPL and call `generate_measurements()` or `start_streaming(url)` to exercise measurement logic without the UI.
- Import CSV scenarios: `data/importer.import_scenario_data(scenario, scenario_name, workspace_dir='workspace', agg_method='lowest')` — see `data/importer.py` for expected CSV columns and aggregation modes.

3) Important conventions & patterns (project-specific)
- Stations: two main classes — `station.Anchor` and `station.Tag` (in `simulation/station.py`). `Scenario` keeps `self.stations` with a mix of anchors and tags; helpers: `get_anchor_list()`, `get_tag_list()`, `get_station_by_name(name)`.
- Measurements: stored in `scenario.measurements` (type `simulation.measurements.Measurements`). Use `measurements.update_relation(frozenset([anchor, tag]), distance)` to add/update a measurement relation. The importer and scenario both use `frozenset([anchor, tag])` as the key.
- Importer CSV expectations: CSVs should contain an `ap-ssid` column and an `est._range(m)` column. Supported aggregation methods: `newest`, `lowest`, `mean`, `median` (default fallback to `newest`). See `data/importer.py` for how rows are mapped.
- UI update model: `presentation.MainWindow.start_periodic_update()` sets up a `QTimer` to call `update_all()`. Note: the timer currently lacks an interval/start call (TODO in code) — tests and patches should verify/adjust this.
- Display: plotting uses `presentation/TrilatPlot` and Matplotlib FigureCanvas (`FigureCanvasQTAgg`). Tabs interact with the `MainWindow` instance to read `scenario` state and call `plot.update_plot()`.

4) Integration points & external dependencies
- PyQt5 GUI (`presentation/`), matplotlib (`presentation/trilatplot.py`), numpy/pandas for numeric work, `sseclient-py` and `requests` for streaming/HTTP.
- Workspace data lives under `workspace/` with CSVs named like `rtt-log-YYYY...csv` and `scenario.json` files. `data/import_measurements.py` and `data/import_scenario.py` are the entry points used by the importer.

5) Code-editing guidance and examples
- To add a new anchor programmatically:
  - from `simulation import station`
  - `scenario.stations.append(station.Anchor([x,y], 'Anchor Name'))`
  - call `scenario.generate_measurements(tag_estimate, tag_truth)` to regenerate measurement relations for a tag.
- To import a CSV scenario (example):
  - `from data.importer import import_scenario_data`
  - `ok, msg = import_scenario_data(scenario, 'example_0', workspace_dir='workspace', agg_method='lowest')`

6) Files to read when changing behavior
- `simulation/scenario.py` — scenario lifecycle, station lists, streaming start/stop.
- `simulation/measurements.py` — internal storage and API for measurement relations.
- `presentation/mainwindow.py` and `presentation/tabs/*` — UI wiring and update paths.
- `data/importer.py` and `data/import_measurements.py` — CSV format expectations and parsing.

7) Tests & quality
- There are no automated tests in the repo. When adding logic, include small, focused unit tests alongside the changed modules (prefer pytest + small fixtures) and validate by running them locally.

8) Quick notes for contributors
- Keep UI logic in `presentation/` and domain logic in `simulation/` — the codebase intentionally separates these.
- Measurement keys use `frozenset([anchor, tag])` — preserve this shape when interacting with `Measurements`.
- Watch for UI timer behavior (see the TODO in `presentation/mainwindow.py`) when implementing streaming-driven updates.

If any part is unclear or you want more examples (e.g., typical DataFrame shapes from CSV import), tell me which area to expand and I will iterate.
