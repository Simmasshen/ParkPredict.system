"""
ParkPredict — Analytics Service
==================================
Uses Pandas to process raw database data into chart-ready summaries.
"""

import pandas as pd


def build_peak_hours_summary(raw_data: list) -> dict:
    """
    Process raw peak hour data into a chart-friendly format.
    Groups by hour across all zones and all days.

    Args:
      raw_data : output of get_peak_hours() from Nitesh's db

    Returns:
      dict with:
        by_hour   → list of { hour, total_checkins } for bar chart
        by_day    → list of { day, total_checkins } for bar chart
        busiest_hour → the hour with the most check-ins
        busiest_day  → the day with the most check-ins
    """
    if not raw_data:
        return {"by_hour": [], "by_day": [], "busiest_hour": None, "busiest_day": None}

    df = pd.DataFrame(raw_data)

    # Group by hour
    by_hour = (
        df.groupby("hour_of_day")["total_checkins"]
        .sum()
        .reset_index()
        .rename(columns={"hour_of_day": "hour", "total_checkins": "total"})
        .sort_values("hour")
    )

    # Group by day
    day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    by_day = (
        df.groupby("day_of_week")["total_checkins"]
        .sum()
        .reset_index()
        .rename(columns={"day_of_week": "day", "total_checkins": "total"})
    )
    by_day["day"] = pd.Categorical(by_day["day"], categories=day_order, ordered=True)
    by_day = by_day.sort_values("day")

    busiest_hour = int(by_hour.loc[by_hour["total"].idxmax(), "hour"]) if not by_hour.empty else None
    busiest_day  = str(by_day.loc[by_day["total"].idxmax(), "day"])    if not by_day.empty  else None

    return {
        "by_hour":      by_hour.to_dict(orient="records"),
        "by_day":       by_day.to_dict(orient="records"),
        "busiest_hour": busiest_hour,
        "busiest_day":  busiest_day,
    }


def build_summary_stats(zones: list) -> dict:
    """
    Calculate overall summary statistics for the dashboard header.

    Args:
      zones : output of get_all_zones() from Nitesh's db

    Returns:
      dict with total_zones, total_slots, occupied_slots,
               available_slots, occupancy_rate_percent
    """
    if not zones:
        return {}

    df = pd.DataFrame(zones)

    total_slots    = int(df["total_slots"].sum())
    available      = int(df["available_slots"].sum())
    occupied       = total_slots - available
    occupancy_rate = round((occupied / total_slots) * 100, 1) if total_slots > 0 else 0.0

    return {
        "total_zones":           len(zones),
        "total_slots":           total_slots,
        "occupied_slots":        occupied,
        "available_slots":       available,
        "occupancy_rate_percent": occupancy_rate,
    }
