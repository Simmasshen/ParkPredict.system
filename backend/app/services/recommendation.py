"""
ParkPredict — Recommendation Service
=======================================
Decision logic for selecting the best parking zone.

Uses a scoring system combining:
  1. Live availability (40%) — how many slots are free right now
  2. Historical probability (40%) — based on past data for this day/hour
  3. Capacity score (20%) — prefer larger zones (more slots = more options)
"""

from datetime import datetime
import pandas as pd


def get_best_zone(zones: list, historical: list, recent_zones: list = []) -> dict:
    """
    Score all zones and return the best recommendation.

    Args:
      zones        : live zone data from get_all_zones()
      historical   : prediction data from get_prediction_data()
      recent_zones : list of zone_ids the user recently visited (to deprioritize)

    Returns:
      dict with:
        recommended_zone → the single best zone with reason
        all_zones_ranked → all zones sorted by score (best first)
    """
    now         = datetime.now()
    current_day = now.strftime("%A")
    current_hr  = now.hour

    # Build historical lookup: zone_id → avg_entries_per_day for this slot
    avg_lookup = {}
    if historical:
        df       = pd.DataFrame(historical)
        filtered = df[
            (df["day_of_week"] == current_day) &
            (df["hour_of_day"] == current_hr)
        ]
        if not filtered.empty:
            for _, row in filtered.iterrows():
                avg_lookup[int(row["zone_id"])] = float(row["avg_entries_per_day"])

    scored = []
    for zone in zones:
        zone_id   = zone["zone_id"]
        total     = zone["total_slots"]
        available = zone["available_slots"]
        status    = zone["status"]

        # Skip unavailable zones
        if status == "maintenance" or available == 0:
            scored.append({**zone, "score": 0, "probability": 0,
                           "reason": "Zone unavailable"})
            continue

        # ── Score 1: Live availability (0–100) ───────────────────────────
        live_score = round((available / total) * 100) if total > 0 else 0

        # ── Score 2: Historical probability (0–100) ──────────────────────
        avg = avg_lookup.get(zone_id)
        if avg is not None and total > 0:
            hist_occupancy = min(avg / total, 1.0)
            hist_score     = round((1 - hist_occupancy) * 100)
        else:
            hist_score = live_score   # fallback to live if no history

        # ── Score 3: Capacity score (0–100) ──────────────────────────────
        # Prefer zones with more total slots — more buffer
        max_total    = max(z["total_slots"] for z in zones)
        capacity_score = round((total / max_total) * 100) if max_total > 0 else 0

        # ── Weighted final score ──────────────────────────────────────────
        final_score = round(
            (live_score     * 0.40) +
            (hist_score     * 0.40) +
            (capacity_score * 0.20)
        )

        # Slight penalty if user recently visited this zone
        if zone_id in recent_zones:
            final_score = max(0, final_score - 15)

        # ── Blended probability (shown to user) ──────────────────────────
        probability = round((live_score * 0.6) + (hist_score * 0.4))

        scored.append({
            "zone_id":        zone_id,
            "zone_name":      zone["zone_name"],
            "location":       zone["location"],
            "available_slots": available,
            "total_slots":    total,
            "status":         status,
            "probability":    probability,
            "score":          final_score,
            "reason":         _reason(live_score, hist_score, available, total),
        })

    # Sort by score descending
    scored.sort(key=lambda x: x["score"], reverse=True)

    # Best zone is the top result
    best = scored[0] if scored else None

    # Clean up score from response (internal use only)
    all_ranked = [{k: v for k, v in z.items() if k != "score"} for z in scored]
    recommended = {k: v for k, v in best.items() if k != "score"} if best else None

    return {
        "recommended_zone":  recommended,
        "all_zones_ranked":  all_ranked,
        "generated_at":      datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "based_on":          f"{current_day} at {current_hr}:00",
    }


def _reason(live_score: int, hist_score: int, available: int, total: int) -> str:
    """Generate a human-readable reason for the recommendation."""
    pct = round((available / total) * 100) if total > 0 else 0

    if live_score >= 70 and hist_score >= 70:
        return f"Best choice — {available} slots free and historically quiet at this hour."
    elif live_score >= 70:
        return f"{available} slots available right now."
    elif hist_score >= 70:
        return f"Historically low traffic at this hour. {available} slots free."
    elif pct >= 40:
        return f"Moderate availability — {available} of {total} slots free."
    else:
        return f"Limited availability — only {available} slots left."
