"""
selection.py - Vintage selection logic with strict zero look-ahead bias.

Rules:
- For delivery day D, cutoff is at cutoff_hour:cutoff_minute in Europe/London on D-1.
- For each delivery period, select the latest forecast where publishTime <= cutoff.
- No look-ahead: forecasts published after the cutoff are strictly excluded.
- Evaluates the 744 hourly delivery periods where both actuals and forecasts exist.
- Identifies and flags missing periods and any duplicate publications.
"""

from datetime import datetime, date, time, timedelta, timezone
from zoneinfo import ZoneInfo
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
import pandas as pd
import numpy as np


@dataclass(frozen=True)
class CutoffConfig:
    """Configurable decision cutoff settings."""
    hour: int = 9
    minute: int = 0
    timezone_name: str = "Europe/London"


def get_cutoff_for_delivery_day(
    delivery_date: date,
    cutoff_hour: int = 9,
    cutoff_minute: int = 0,
    timezone_name: str = "Europe/London"
) -> datetime:
    """
    Calculate the decision cutoff timestamp in UTC for a given delivery day D.
    The cutoff occurs on day D - 1 at the specified local time in Europe/London.
    """
    tz = ZoneInfo(timezone_name)
    d_minus_1 = delivery_date - timedelta(days=1)
    local_cutoff = datetime(
        d_minus_1.year,
        d_minus_1.month,
        d_minus_1.day,
        cutoff_hour,
        cutoff_minute,
        0,
        tzinfo=tz
    )
    return local_cutoff.astimezone(timezone.utc)


def select_cutoff_forecasts(
    df_actuals: pd.DataFrame,
    df_forecasts: pd.DataFrame,
    cutoff_hour: int = 9,
    cutoff_minute: int = 0,
    timezone_name: str = "Europe/London"
) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Join actuals with the latest eligible forecast vintage published on or before the cutoff.
    
    Args:
        df_actuals: DataFrame of actual wind outturns with columns ['startTime', 'generation', ...].
        df_forecasts: DataFrame of wind forecasts with columns ['startTime', 'publishTime', 'generation', ...].
        cutoff_hour: Hour of assumed decision cutoff on D-1 in Europe/London (default: 9).
        cutoff_minute: Minute of assumed decision cutoff on D-1 in Europe/London (default: 0).
        timezone_name: Timezone string (default: 'Europe/London').

    Returns:
        (df_matched, metadata_dict)
    """
    tz = ZoneInfo(timezone_name)

    # 1. Separate forward forecasts (leadTime >= 0) to avoid hindcast/initialization points
    if "isNegativeLeadTime" in df_forecasts.columns:
        f_clean = df_forecasts[~df_forecasts["isNegativeLeadTime"]].copy()
    else:
        # Calculate on the fly if needed
        f_clean = df_forecasts[df_forecasts["startTime"] >= df_forecasts["publishTime"]].copy()

    # Pre-index forecast candidates by startTime -> list of dicts
    # Each item: {'publishTime': pt, 'generation': gen, 'leadTimeHours': lt}
    f_by_start: Dict[str, List[Dict[str, Any]]] = {}
    for _, row in f_clean.iterrows():
        st = row["startTime"]
        item = {
            "publishTime": row["publishTime"],
            "generation": float(row["generation"]),
            "leadTimeHours": float(row.get("leadTimeHours", 0.0))
        }
        f_by_start.setdefault(st, []).append(item)

    # 2. Iterate through all delivery actuals
    matched_rows = []
    hourly_expected = 0
    hourly_matched = 0
    duplicate_pub_periods = []
    missing_hourly_periods = []

    for _, a_row in df_actuals.iterrows():
        st_str = a_row["startTime"]
        st_utc = datetime.fromisoformat(st_str.replace("Z", "+00:00"))
        st_local = st_utc.astimezone(tz)
        delivery_day = st_local.date()
        is_hourly = st_str.endswith(":00:00Z")

        # Cutoff in UTC for delivery day D
        cutoff_utc = get_cutoff_for_delivery_day(delivery_day, cutoff_hour, cutoff_minute, timezone_name)
        cutoff_utc_str = cutoff_utc.strftime("%Y-%m-%dT%H:%M:%SZ")

        if is_hourly:
            hourly_expected += 1

        # Find eligible forecasts published on or before cutoff
        candidates = [
            cand for cand in f_by_start.get(st_str, [])
            if cand["publishTime"] <= cutoff_utc_str
        ]

        selected_forecast: Optional[float] = None
        selected_publish_time: Optional[str] = None
        selected_lead_time: Optional[float] = None
        has_forecast = False
        has_duplicate_pub = False

        if candidates:
            # Sort chronologically by publishTime
            candidates.sort(key=lambda x: x["publishTime"])
            latest_pt = candidates[-1]["publishTime"]
            
            # Check for duplicate publication at the exact same max publishTime
            duplicates_at_max = [c for c in candidates if c["publishTime"] == latest_pt]
            if len(duplicates_at_max) > 1:
                has_duplicate_pub = True
                duplicate_pub_periods.append(st_str)

            selected_cand = candidates[-1]
            selected_forecast = selected_cand["generation"]
            selected_publish_time = selected_cand["publishTime"]
            selected_lead_time = selected_cand["leadTimeHours"]
            has_forecast = True

            if is_hourly:
                hourly_matched += 1
        else:
            if is_hourly:
                missing_hourly_periods.append(st_str)

        actual_gen = float(a_row["generation"])
        error = (selected_forecast - actual_gen) if selected_forecast is not None else None
        abs_error = abs(error) if error is not None else None

        matched_rows.append({
            "startTime": st_str,
            "startTimeUK": st_local.strftime("%Y-%m-%d %H:%M:%S"),
            "deliveryDate": str(delivery_day),
            "settlementDate": a_row.get("settlementDate", str(delivery_day)),
            "settlementPeriod": int(a_row.get("settlementPeriod", 0)),
            "isHourlyPeriod": is_hourly,
            "cutoffTimeUTC": cutoff_utc_str,
            "actual": actual_gen,
            "forecast": selected_forecast,
            "error": error,
            "absError": abs_error,
            "publishTime": selected_publish_time,
            "leadTimeHours": selected_lead_time,
            "hasForecast": has_forecast,
            "hasDuplicatePublication": has_duplicate_pub
        })

    df_result = pd.DataFrame(matched_rows)

    metadata = {
        "cutoffAssumption": f"{cutoff_hour:02d}:{cutoff_minute:02d} {timezone_name} on D-1",
        "totalActualPeriods": len(df_actuals),
        "expectedHourlyPeriods": hourly_expected,
        "matchedHourlyPeriods": hourly_matched,
        "hourlyCoveragePct": round((hourly_matched / hourly_expected * 100.0), 2) if hourly_expected > 0 else 0.0,
        "halfHourPeriodsWithoutForecast": len(df_actuals) - hourly_expected,
        "missingHourlyPeriods": missing_hourly_periods,
        "duplicatePublicationCount": len(duplicate_pub_periods)
    }

    return df_result, metadata
