"""
ParkPredict — Prediction Service
==================================
Uses Pandas to calculate parking availability probability
based on historical data from Nitesh's database.
"""

from datetime import datetime
import pandas as pd


def predict_availability(raw_data: list, zones: list) -> list:
    """
    Predict the probability of finding a parking spot right now,
    for each zone, based on historical average entries per hour.

    Args:
      raw_data : output of get_prediction_data() from Nitesh's db
      zones    : output of get_all_zones() from Nitesh's db

    Returns:
      List of dicts:
        zone_id, zone_name, available_slots, total_slots,
        probability (0–100), suggestion
    """
    if not raw_data:
        return _no_data_fallback(zones)

    now         = datetime.now()
    current_day = now.strftime("%A")   # e.g. 'Monday'
    current_hr  = now.hour             # 0–23

    df = pd.DataFrame(raw_data)

    # Filter to current day + hour
    filtered = df[
        (df["day_of_week"] == current_day) &
        (df["hour_of_day"] == current_hr)
    ]

    # Build a lookup: zone_id → avg_entries_per_day at this slot
    avg_lookup = {}
    if not filtered.empty:
        for _, row in filtered.iterrows():
            avg_lookup[int(row["zone_id"])] = float(row["avg_entries_per_day"])

    results = []
    for zone in zones:
        zone_id    = zone["zone_id"]
        total      = zone["total_slots"]
        available  = zone["available_slots"]

        # Base probability from live slot count
        live_prob = round((available / total) * 100) if total > 0 else 0

        # Adjust using historical average for this hour (if data exists)
        avg = avg_lookup.get(zone_id)
        if avg is not None and total > 0:
            historical_occupancy = min(avg / total, 1.0)
            # Blend: 60% live data, 40% historical
            blended_prob = round((live_prob * 0.6) + ((1 - historical_occupancy) * 100 * 0.4))
            probability  = max(0, min(100, blended_prob))
        else:
            probability = live_prob

        results.append({
            "zone_id":        zone_id,
            "zone_name":      zone["zone_name"],
            "location":       zone["location"],
            "available_slots": available,
            "total_slots":    total,
            "probability":    probability,
            "suggestion":     _suggestion(probability),
        })

    return results


def _suggestion(probability: int) -> str:
    """Return a human-friendly suggestion based on probability."""
    if probability >= 70:
        return "Good chance of finding a spot. Go now!"
    elif probability >= 40:
        return "Moderate chance. Try to arrive soon."
    elif probability >= 15:
        return "Low chance. Consider an alternative zone."
    else:
        return "Very unlikely. Choose a different zone."


def _no_data_fallback(zones: list) -> list:
    """Return live-only probability when no historical data exists yet."""
    results = []
    for zone in zones:
        total      = zone["total_slots"]
        available  = zone["available_slots"]
        probability = round((available / total) * 100) if total > 0 else 0
        results.append({
            "zone_id":         zone["zone_id"],
            "zone_name":       zone["zone_name"],
            "location":        zone["location"],
            "available_slots": available,
            "total_slots":     total,
            "probability":     probability,
            "suggestion":      _suggestion(probability),
        })
    return results
