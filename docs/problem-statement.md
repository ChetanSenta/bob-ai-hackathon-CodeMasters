# Problem Statement

## Who This Is For

**Primary audience: Military maintenance supervisors and crew chiefs** responsible for declaring assets mission-ready before a sortie or deployment window. These personnel must sign off on the airworthiness of helicopters, the mechanical status of armoured vehicles, and the readiness of fixed-wing platforms — often within 12–24 hours of a mission brief. They need a fast, authoritative answer to a single question: *"Which of my assets are not ready, and what do I need to fix first?"*

**Secondary audience: Fleet maintenance officers** who plan maintenance schedules across a full squadron or battalion and need to forecast parts, labour, and downtime days or weeks in advance.

Neither group has time to run database queries or interpret raw sensor exports. They need a system that speaks their language: tail numbers, component names, urgency levels, and time-to-mission.

---

## The Core Problem

Military aircraft and ground vehicles — Apache attack helicopters, CH-47 Chinooks, M1 Abrams tanks, Bradley fighting vehicles — are equipped with **Health & Usage Monitoring Systems (HUMS)**. These sensor arrays continuously collect telemetry: rotor vibration frequencies, engine temperatures, hydraulic pressures, oil quality indices, and cycle counts. The technical infrastructure to detect failures weeks before they happen already exists.

**It goes unused.**

Military maintenance operations run predominantly on **fixed time-based service schedules**: inspect every 100 flight hours, change oil every 250 hours, overhaul the engine at 500 hours — regardless of what the sensors say. HUMS data is ingested into specialist platforms (ALIS, IMDS, LIMS-EV) and stored, but it sits largely unanalysed between scheduled reviews. The result is a dual failure mode:

### 1. Over-maintenance
Serviceable components are pulled from service on calendar schedule. Technicians perform inspections that find nothing wrong. Platforms are unavailable during servicing windows even though they are mechanically sound. Resources are consumed without benefit.

### 2. Under-maintenance
Components showing early degradation signatures — a rotor vibration reading trending upward, an oil quality index that has dropped 30 points over six weeks — are not flagged for inspection because the *next scheduled service is still weeks away*. The anomaly sits in a database no-one is actively watching. The component fails in the field.

---

## Why Calendar Maintenance Fails

Calendar-based maintenance was designed for an era before pervasive sensor telemetry. It provides a minimum safety guarantee: if you service everything at the prescribed interval, most components will not fail between services. But it optimises for the *average* component in the *average* operating environment.

Modern military operations are not average:
- Helicopters deployed to high-altitude, high-temperature environments (e.g. Afghanistan, Middle East) experience rotor and engine stress at 2–3× the rate assumed by sea-level maintenance intervals
- Armoured vehicles operating on rough terrain accumulate drivetrain wear faster than those on prepared roads
- Usage varies radically between training rotations and combat deployments

A sensor that shows a rotor vibration at 8 mm/s — exceeding the RED threshold — tells you the component needs attention *now*, regardless of when it was last serviced. Calendar schedules cannot make this call. Condition-based monitoring can.

---

## Quantified Cost

- The US Department of Defense spends approximately **$90 billion per year** on operations and maintenance for aviation and ground systems (DoD FY2024 President's Budget)
- Industry analysis from the Government Accountability Office and RAND Corporation estimates that **shifting to condition-based maintenance could reduce costs by 10–25%** — representing $9–22B in annual savings
- A single unexpected grounding of a mission-critical rotary-wing asset (medevac, fire support, ISR) can delay or abort a mission with direct operational and **life-safety consequences**
- Maintenance crew chiefs spend an estimated **2–4 hours per shift** manually cross-referencing paper logs, digital sensor exports, and maintenance management systems to produce a readiness report — time that becomes available for actual maintenance work with automated analysis

---

## Why Existing Tools Don't Solve It

Current HUMS data management platforms are designed for **data archival and compliance reporting**, not real-time mission readiness decision support:

| Tool | What it does well | What it cannot do |
|------|-------------------|-------------------|
| ALIS / IMDS | Stores HUMS records, tracks scheduled maintenance, manages parts inventory | Proactively surfaces anomalies, answers natural-language questions, ranks by mission proximity |
| HUMS post-processing tools | Generates vibration spectra and health indices for trained analysts | Used by specialists only; output requires interpretation; not integrated with mission schedules |
| Manual readiness report | Crew chief experience captures local knowledge | Takes hours, depends on individual, not repeatable |

There is no existing tool that answers: *"Given tomorrow's 0600Z mission window, which components across my 25-asset fleet will fail before then, and in what order should I fix them?"*

That is the gap this project fills.
