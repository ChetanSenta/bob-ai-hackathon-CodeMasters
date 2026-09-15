"""
Rules engine: component threshold scoring.

Each metric is evaluated against fixed thresholds and mapped to:
  - A status band: GREEN / AMBER / RED
  - A score 0–100  (100 = perfect, 0 = critical)

Asset-level status = worst individual component status.
Asset-level score  = minimum individual component score.
"""
from __future__ import annotations

from typing import Dict, List, Optional, Tuple

# ---------------------------------------------------------------------------
# Threshold table
# (lower_bound, upper_bound) — None means unbounded in that direction.
# For oil_quality_index, lower is worse (inverted scale).
# ---------------------------------------------------------------------------

THRESHOLDS: Dict[str, Dict[str, Tuple[Optional[float], Optional[float]]]] = {
    "vibration_mm_s": {
        "GREEN": (None, 4.0),
        "AMBER": (4.0, 7.0),
        "RED":   (7.0, None),
    },
    "engine_temp_c": {
        "GREEN": (None, 180.0),
        "AMBER": (180.0, 220.0),
        "RED":   (220.0, None),
    },
    "oil_quality_index": {
        # lower is worse — bands are reversed
        "GREEN": (60.0, None),
        "AMBER": (40.0, 60.0),
        "RED":   (None, 40.0),
    },
    "hours_since_last_service": {
        "GREEN": (None, 200.0),
        "AMBER": (200.0, 350.0),
        "RED":   (350.0, None),
    },
}

# Maintenance action templates keyed by metric
_ACTIONS: Dict[str, str] = {
    "vibration_mm_s":           "Rotor balance inspection and dynamic balancing",
    "engine_temp_c":            "Engine cooling system inspection and thermal regulation service",
    "oil_quality_index":        "Hydraulic oil flush and filter replacement",
    "hours_since_last_service": "Overdue scheduled maintenance — full component inspection required",
}

_RECOMMENDATIONS: Dict[str, str] = {
    "vibration_mm_s":           "Immediate rotor balance inspection required",
    "engine_temp_c":            "Immediate engine cooling inspection required",
    "oil_quality_index":        "Hydraulic oil replacement required before next sortie",
    "hours_since_last_service": "Asset is overdue for scheduled service — ground until inspected",
}

_DURATION: Dict[str, float] = {
    "vibration_mm_s":           8.0,
    "engine_temp_c":            6.0,
    "oil_quality_index":        4.0,
    "hours_since_last_service": 10.0,
}

STATUS_PRIORITY = {"RED": 2, "AMBER": 1, "GREEN": 0}


def _in_band(value: float, bounds: Tuple[Optional[float], Optional[float]]) -> bool:
    lo, hi = bounds
    if lo is not None and value < lo:
        return False
    if hi is not None and value >= hi:
        return False
    return True


def score_metric(metric_name: str, value: float) -> Tuple[str, int]:
    """
    Return (status, score) for a single metric value.

    Status: GREEN / AMBER / RED
    Score:  0–100 (100 = perfect health, 0 = critical)

    For unknown metrics returns ("GREEN", 100).
    """
    bands = THRESHOLDS.get(metric_name)
    if bands is None:
        return ("GREEN", 100)

    status = "GREEN"
    for band_name in ("RED", "AMBER", "GREEN"):
        if _in_band(value, bands[band_name]):
            status = band_name
            break

    # -----------------------------------------------------------------------
    # Scoring: linearly interpolate within the range that spans all bands.
    # GREEN → 70–100, AMBER → 30–69, RED → 0–29
    # -----------------------------------------------------------------------
    score = _compute_score(metric_name, value, status)
    return (status, score)


def _compute_score(metric_name: str, value: float, status: str) -> int:
    """
    Map a metric value to an integer score 0–100.

    Strategy:
      - Identify the "safe" anchor (GREEN boundary) and "danger" anchor
        (beyond-RED boundary, estimated at 2× the RED threshold).
      - Linearly interpolate between safe (100) and danger (0).
      - Clamp to [0, 100].
    """
    bands = THRESHOLDS[metric_name]

    # Determine direction: "higher is worse" vs "lower is worse"
    green_lo, green_hi = bands["GREEN"]
    red_lo, red_hi = bands["RED"]

    if green_hi is not None and red_lo is not None:
        # Higher is worse (vibration, engine_temp, hours_since_service)
        safe_val = green_hi            # top of GREEN
        danger_val = red_lo * 1.5     # well into RED
        ratio = (value - safe_val) / (danger_val - safe_val)
    elif green_lo is not None and red_hi is not None:
        # Lower is worse (oil_quality_index)
        safe_val = green_lo
        danger_val = max(red_hi * 0.5, 1.0)   # well into RED (low)
        ratio = (safe_val - value) / (safe_val - danger_val)
    else:
        # Fallback
        ratio = 0.0 if status == "GREEN" else (0.5 if status == "AMBER" else 0.9)

    ratio = max(0.0, min(1.0, ratio))
    score = round(100 - ratio * 100)
    return score


# ---------------------------------------------------------------------------
# Public helpers
# ---------------------------------------------------------------------------

def score_asset_components(readings: List[dict]) -> List[dict]:
    """
    Given a list of sensor reading dicts (each with 'metric_name', 'value',
    'component'), return a list of component-level status dicts.

    When multiple readings share the same component, the worst one wins.
    """
    # Keep worst reading per component
    worst: Dict[str, dict] = {}
    for r in readings:
        metric = r.get("metric_name", "")
        if metric not in THRESHOLDS:
            continue
        comp = r.get("component") or metric
        status, score = score_metric(metric, float(r["value"]))
        existing = worst.get(comp)
        if existing is None or STATUS_PRIORITY[status] > STATUS_PRIORITY[existing["status"]]:
            worst[comp] = {
                "component": comp,
                "metric": metric,
                "value": float(r["value"]),
                "status": status,
                "score": score,
            }

    return list(worst.values())


def asset_overall(components: List[dict]) -> Tuple[str, int]:
    """
    Derive the overall asset status and score from a list of component dicts.
    Returns ("GREEN", 100) when there are no scored components.
    """
    if not components:
        return ("GREEN", 100)

    worst_status = max(
        (c["status"] for c in components),
        key=lambda s: STATUS_PRIORITY[s],
    )
    lowest_score = min(c["score"] for c in components)
    return (worst_status, lowest_score)


def get_red_threshold(metric_name: str) -> Optional[float]:
    """Return the scalar RED boundary for a metric, or None if not defined."""
    bands = THRESHOLDS.get(metric_name)
    if bands is None:
        return None
    lo, hi = bands["RED"]
    # "higher is worse" → lo is the RED boundary
    if lo is not None:
        return lo
    # "lower is worse" → hi is the RED boundary
    return hi


def get_action(metric_name: str) -> str:
    return _ACTIONS.get(metric_name, "Inspect and service component")


def get_recommendation(metric_name: str) -> str:
    return _RECOMMENDATIONS.get(metric_name, "Component requires inspection")


def get_duration(metric_name: str) -> float:
    return _DURATION.get(metric_name, 4.0)
