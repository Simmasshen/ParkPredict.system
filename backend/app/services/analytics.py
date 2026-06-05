"""
ParkPredict — Analytics Service
==================================
Uses Pandas to process raw database data into chart-ready summaries.

Functions:
  build_summary_stats(zones)           → dashboard header stats
  build_peak_hours_summary(raw, zone)  → peak hours bar chart data
  build_usage_trends(raw)              → per-zone usage line chart data
  build_zone_comparison(raw, zones)    → zone comparison table data
"""

import pandas as pd


# ── SUMMARY STATS ─────────────────────────────────────────────────────────

def build_summary_stats(zones: list) -> dict:
    """
    Overall summary for the dashboard header.

    Returns:
      total_zones, total_slots, occupied_slots,
      available_slots, occupancy_rate_percent
    """
    if not zones:
        return {}

    df             = pd.DataFrame(zones)
    total_slots    = int(df["total_slots"].sum())
    available      = int(df["available_slots"].sum())
    occupied       = total_slots - available
    occupancy_rate = round((occupied / total_slots) * 100, 1) if total_slots > 0 else 0.0

    return {
        "total_zones":            len(zones),
        "total_slots":            total_slots,
        "occupied_slots":         occupied,
        "available_slots":        available,
        "occupancy_rate_percent": occupancy_rate,
    }


# ── PEAK HOURS ────────────────────────────────────────────────────────────

def build_peak_hours_summary(raw_data: list, zone_id: int = None) -> dict:
    """
    Process raw peak hour data into chart-friendly format.

    Args:
      raw_data : output of get_peak_hours() from Nitesh's db
      zone_id  : optional — filter to one zone only

    Returns:
      by_hour      → [ { hour, total } ] sorted 0–23   (for bar chart)
      by_day       → [ { day,  total } ] sorted Mon–Sun (for bar chart)
      busiest_hour → hour number with most check-ins
      busiest_day  → day name with most check-ins
      by_zone_hour → [ { zone_id, hour, total } ]       (for grouped chart)
    """
    if not raw_data:
        return {
            "by_hour": [], "by_day": [],
            "busiest_hour": None, "busiest_day": None,
            "by_zone_hour": []
        }

    df = pd.DataFrame(raw_data)

    # Filter by zone if requested
    if zone_id:
        df = df[df["zone_id"] == zone_id]

    if df.empty:
        return {
            "by_hour": [], "by_day": [],
            "busiest_hour": None, "busiest_day": None,
            "by_zone_hour": []
        }

    # Group by hour (all zones combined)
    by_hour = (
        df.groupby("hour_of_day")["total_checkins"]
        .sum().reset_index()
        .rename(columns={"hour_of_day": "hour", "total_checkins": "total"})
        .sort_values("hour")
    )

    # Group by day
    day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    by_day = (
        df.groupby("day_of_week")["total_checkins"]
        .sum().reset_index()
        .rename(columns={"day_of_week": "day", "total_checkins": "total"})
    )
    by_day["day"] = pd.Categorical(by_day["day"], categories=day_order, ordered=True)
    by_day = by_day.sort_values("day")

    # Per-zone per-hour breakdown (for grouped bar chart)
    by_zone_hour = (
        df.groupby(["zone_id", "hour_of_day"])["total_checkins"]
        .sum().reset_index()
        .rename(columns={"hour_of_day": "hour", "total_checkins": "total"})
        .sort_values(["zone_id", "hour"])
    )

    busiest_hour = int(by_hour.loc[by_hour["total"].idxmax(), "hour"]) if not by_hour.empty else None
    busiest_day  = str(by_day.loc[by_day["total"].idxmax(),  "day"])   if not by_day.empty  else None

    return {
        "by_hour":      by_hour.to_dict(orient="records"),
        "by_day":       by_day.to_dict(orient="records"),
        "busiest_hour": busiest_hour,
        "busiest_day":  busiest_day,
        "by_zone_hour": by_zone_hour.to_dict(orient="records"),
    }


# ── USAGE TRENDS ──────────────────────────────────────────────────────────

def build_usage_trends(raw_data: list) -> dict:
    """
    Process usage trends per zone — for line charts.
    Shows which zones are busiest at each hour across the week.

    Returns:
      zones         → list of zone_ids found in data
      hourly_trend  → [ { hour, zone_id, avg_checkins } ] (line chart)
      daily_trend   → [ { day, zone_id, total_checkins } ] (line chart)
      summary       → [ { zone_id, total_checkins, peak_hour, peak_day } ]
    """
    if not raw_data:
        return {"zones": [], "hourly_trend": [], "daily_trend": [], "summary": []}

    df        = pd.DataFrame(raw_data)
    zone_ids  = sorted(df["zone_id"].unique().tolist())

    # Hourly trend per zone
    hourly_trend = (
        df.groupby(["zone_id", "hour_of_day"])["total_checkins"]
        .sum().reset_index()
        .rename(columns={"hour_of_day": "hour", "total_checkins": "total"})
        .sort_values(["zone_id", "hour"])
    )

    # Daily trend per zone
    day_order    = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    daily_trend  = (
        df.groupby(["zone_id", "day_of_week"])["total_checkins"]
        .sum().reset_index()
        .rename(columns={"day_of_week": "day", "total_checkins": "total"})
    )
    daily_trend["day"] = pd.Categorical(daily_trend["day"], categories=day_order, ordered=True)
    daily_trend = daily_trend.sort_values(["zone_id", "day"])

    # Per-zone summary
    summary_rows = []
    for zid in zone_ids:
        zone_df   = df[df["zone_id"] == zid]
        total     = int(zone_df["total_checkins"].sum())

        peak_hour_row = zone_df.loc[zone_df["total_checkins"].idxmax()]
        peak_hour = int(peak_hour_row["hour_of_day"])
        peak_day  = str(peak_hour_row["day_of_week"])

        summary_rows.append({
            "zone_id":        zid,
            "total_checkins": total,
            "peak_hour":      peak_hour,
            "peak_day":       peak_day,
        })

    return {
        "zones":        zone_ids,
        "hourly_trend": hourly_trend.to_dict(orient="records"),
        "daily_trend":  daily_trend.to_dict(orient="records"),
        "summary":      summary_rows,
    }


# ── ZONE COMPARISON ───────────────────────────────────────────────────────

def build_zone_comparison(raw_data: list, zones: list) -> list:
    """
    Side-by-side comparison of all zones.
    Shows total entries, avg duration, peak hour, and current live status.

    Returns:
      List of dicts per zone:
        zone_id, zone_name, location, total_slots, available_slots,
        status, total_entries, avg_duration_min, peak_hour, peak_day,
        avg_entries_per_day, occupancy_rate_percent
    """
    if not zones:
        return []

    zones_df = pd.DataFrame(zones)

    if not raw_data:
        # Return live data only if no historical data yet
        result = []
        for zone in zones:
            total = zone["total_slots"]
            avail = zone["available_slots"]
            result.append({
                "zone_id":              zone["zone_id"],
                "zone_name":            zone["zone_name"],
                "location":             zone["location"],
                "total_slots":          total,
                "available_slots":      avail,
                "status":               zone["status"],
                "total_entries":        0,
                "avg_duration_min":     0,
                "peak_hour":            None,
                "peak_day":             None,
                "avg_entries_per_day":  0,
                "occupancy_rate_percent": round(((total - avail) / total) * 100, 1) if total > 0 else 0,
            })
        return result

    hist_df = pd.DataFrame(raw_data)

    result = []
    for zone in zones:
        zid   = zone["zone_id"]
        total = zone["total_slots"]
        avail = zone["available_slots"]

        zone_hist = hist_df[hist_df["zone_id"] == zid]

        if not zone_hist.empty:
            total_entries    = int(zone_hist["total_entries"].sum())
            avg_duration     = round(float(zone_hist["avg_duration_min"].mean()), 1)
            avg_per_day      = round(float(zone_hist["avg_entries_per_day"].mean()), 1)
            peak_row         = zone_hist.loc[zone_hist["total_entries"].idxmax()]
            peak_hour        = int(peak_row["hour_of_day"])
            peak_day         = str(peak_row["day_of_week"])
        else:
            total_entries = avg_duration = avg_per_day = 0
            peak_hour = peak_day = None

        result.append({
            "zone_id":                zid,
            "zone_name":              zone["zone_name"],
            "location":               zone["location"],
            "total_slots":            total,
            "available_slots":        avail,
            "status":                 zone["status"],
            "total_entries":          total_entries,
            "avg_duration_min":       avg_duration,
            "peak_hour":              peak_hour,
            "peak_day":               peak_day,
            "avg_entries_per_day":    avg_per_day,
            "occupancy_rate_percent": round(((total - avail) / total) * 100, 1) if total > 0 else 0,
        })

    # Sort by total_entries descending (busiest zone first)
    result.sort(key=lambda x: x["total_entries"], reverse=True)
    return result
