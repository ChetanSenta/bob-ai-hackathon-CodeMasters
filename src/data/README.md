# src/data — Synthetic HUMS Dataset

Synthetic data for the **Mission Readiness Officer** demo.  
All files are produced by running `generate_dataset.py` and are fully reproducible.

---

## How to Regenerate

```bash
python src/data/generate_dataset.py
```

Requires Python 3.9+ (stdlib only — no third-party packages needed).  
The script uses a fixed random seed (`seed=42`) so every run produces
identical output.

---

## Files

| File | Rows / Entries | Description |
|------|---------------|-------------|
| `sample_hums_sensors.csv` | 600 rows | Sensor telemetry snapshots, one metric per row |
| `sample_service_records.csv` | 65 rows | Maintenance history across the fleet |
| `asset_registry.json` | 25 entries | Master list of assets with status and mission window |

---

## Schema: `sample_hums_sensors.csv`

| Column | Type | Description |
|--------|------|-------------|
| `reading_id` | string | Unique ID, e.g. `RD00001` |
| `asset_id` | string | Short asset identifier, e.g. `AH01` |
| `tail_number` | string | Tail number, e.g. `TAIL-AH01` |
| `asset_type` | string | `helicopter` / `fixed_wing` / `ground_vehicle` |
| `platform` | string | Full platform name, e.g. `AH-64 Apache` |
| `timestamp` | ISO 8601 UTC | When the reading was taken |
| `metric_name` | string | One of the four metrics (see below) |
| `value` | float | Sensor reading value |
| `unit` | string | `mm/s` / `celsius` / `index` / `hours` |
| `component` | string | Affected component: `rotor`, `engine`, `hydraulics`, `airframe`, `drivetrain` |

---

## Schema: `sample_service_records.csv`

| Column | Type | Description |
|--------|------|-------------|
| `record_id` | string | Unique ID, e.g. `SR0001` |
| `asset_id` | string | Asset this record belongs to |
| `tail_number` | string | Tail number |
| `component` | string | Component serviced |
| `maintenance_type` | string | `scheduled_inspection` / `component_replacement` / `lubrication` / `calibration` / `unscheduled_repair` |
| `technician` | string | Name and rank of technician |
| `date` | `YYYY-MM-DD` | Date service was performed |
| `notes` | string | Free-text notes from the technician |
| `outcome` | string | `completed` / `parts_on_order` / `deferred` |

---

## Schema: `asset_registry.json`

Each entry in the JSON array has the following fields:

| Field | Type | Description |
|-------|------|-------------|
| `asset_id` | string | Short identifier, e.g. `AH01` |
| `tail_number` | string | Tail number, e.g. `TAIL-AH01` |
| `asset_type` | string | `helicopter` / `fixed_wing` / `ground_vehicle` |
| `platform` | string | Full platform name |
| `unit` | string | Military unit, e.g. `101st Airborne` |
| `base` | string | Home base, e.g. `Fort Campbell` |
| `next_mission_window` | ISO 8601 UTC | Next scheduled mission 2–5 days from 2025-07-15 |
| `current_status` | string | `GREEN` / `AMBER` / `RED` — derived from injected anomalies |

---

## Sensor Metrics & Thresholds

The rules engine in Sub-Task 3 uses these exact thresholds:

| Metric | Unit | GREEN | AMBER | RED |
|--------|------|-------|-------|-----|
| `vibration_mm_s` | mm/s | < 4.0 | 4.0 – 7.0 | > 7.0 |
| `engine_temp_c` | celsius | < 180 | 180 – 220 | > 220 |
| `oil_quality_index` | index | > 60 | 40 – 60 | < 40 |
| `hours_since_last_service` | hours | < 200 | 200 – 350 | > 350 |

---

## Asset Fleet

### Helicopters (10)

| Asset ID | Tail Number | Platform | Unit | Base |
|----------|------------|---------|------|------|
| AH01–AH05 | TAIL-AH01 … TAIL-AH05 | AH-64 Apache | 101st Airborne | Fort Campbell |
| UH01–UH05 | TAIL-UH01 … TAIL-UH05 | UH-60 Black Hawk | 82nd Airborne | Fort Bragg |

### Fixed-Wing Aircraft (8)

| Asset ID | Tail Number | Platform | Unit | Base |
|----------|------------|---------|------|------|
| AW01–AW04 | TAIL-AW01 … TAIL-AW04 | A-10 Thunderbolt II | 23rd Wing | Moody AFB |
| CH01–CH04 | TAIL-CH01 … TAIL-CH04 | C-130 Hercules | 19th Airlift Wing | Little Rock AFB |

### Ground Vehicles (7)

| Asset ID | Tail Number | Platform | Unit | Base |
|----------|------------|---------|------|------|
| MB01–MB04 | TAIL-MB01 … TAIL-MB04 | M1 Abrams | 3rd Infantry Division | Fort Stewart |
| BR01–BR03 | TAIL-BR01 … TAIL-BR03 | M2 Bradley | 4th Infantry Division | Fort Carson |

---

## Injected Anomalies

Five assets have deliberate anomalies to exercise the rules engine and drive
the demo narrative.

| Asset ID | Tail Number | Fault | Metric | Value | Threshold Band | Root Cause |
|----------|------------|-------|--------|-------|---------------|-----------|
| AH04 | TAIL-AH04 | Rotor imbalance | `vibration_mm_s` | **8.2 mm/s** | 🔴 RED (> 7.0) | Damaged rotor blade causing excessive vibration |
| UH03 | TAIL-UH03 | Engine overheating | `engine_temp_c` | **228 °C** | 🔴 RED (> 220) | Blocked cooling duct / failing temperature regulation |
| AW02 | TAIL-AW02 | Oil degradation | `oil_quality_index` | **32** | 🔴 RED (< 40) | Contaminated hydraulic oil — risk of pump failure |
| MB03 | TAIL-MB03 | Overdue service | `hours_since_last_service` | **387 h** | 🔴 RED (> 350) | Previous inspection deferred; no follow-up completed |
| CH04 | TAIL-CH04 | Dual AMBER trend | `vibration_mm_s` = 5.8, `engine_temp_c` = 198 °C | Both **AMBER** | ⚠️ AMBER (trending) | Early-stage compressor wear — escalation risk before mission window |

### Service Record Behaviour for Anomalous Assets

- **AH04, UH03, AW02, CH04** — each has a recent `unscheduled_repair` record with `outcome = deferred`, reflecting a failed repair attempt.
- **MB03** — has a single `scheduled_inspection` record with `outcome = deferred` and no follow-up, representing an overdue maintenance window.

---

## Reference Date

All timestamps are anchored to **2025-07-15T06:00:00Z** as "today".  
Sensor readings span the 7 days prior; service records span the past 12 months.
